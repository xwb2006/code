# BM25 + Bigram
import os
import json
import jieba
import re
import math
import pickle  # 引入 pickle 库用于序列化对象
from collections import defaultdict, Counter

# Posting 类
class Posting(object):
    special_doc_id = -1
    def __init__(self, docid, tf=0):
        self.docid = docid
        self.tf = tf
    def __repr__(self):
        return f"<docid: {self.docid}, tf: {self.tf}>"

class SearchEngine:
    def __init__(self, k1=1.5, b=0.75):
        self.inverted_index = defaultdict(list)
        self.doc_lengths = []
        self.total_docs = 0
        self.doc_info = {}  #读取储存的pkl数据
        self.avg_doc_len = 0.0
        self.k1 = k1
        self.b = b
        # json_dir 不再是类的属性，而是在构建时传入

    def _filter_text(self, text):
        pattern = re.compile(r'[^一-龥a-zA-Z0-9]')
        return pattern.sub('', text).strip()

    @staticmethod
    def _generate_ngrams(tokens, n=2):
        ngrams = zip(*[tokens[i:] for i in range(n)])
        return ["".join(ngram) for ngram in ngrams]

    def build_index_from_json(self, json_dir="wordsegment"):
        """
        从JSON文件目录构建完整的倒排索引。
        """
        if not os.path.exists(json_dir):
            print(f"[ERROR] 目录不存在: {json_dir}")
            return

        json_files = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')])
        if not json_files:
            print(f"[ERROR] 目录 {json_dir} 中没有找到JSON文件。")
            return
            
        print(f"--- 正在从 {len(json_files)} 个JSON文件中加载并构建索引 (含Bigram) ---")

        temp_doc_data = []
        
        for docid, filename in enumerate(json_files):
            file_path = os.path.join(json_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[LOAD ERROR] 读取或解析 {filename} 失败: {e}")
                continue

            self.doc_info[docid] = {
                "title": data.get("page_title", "无标题"),
                "url": data.get("source_url", "未知URL"),
                "full_body_text": data.get("full_body_text", "")
            }
            
            title = data.get("page_title", "")
            body = data.get("full_body_text", "")
            full_text = (title + " ") * 3 + body

            unigrams = [self._filter_text(w) for w in jieba.lcut_for_search(full_text) if self._filter_text(w)]
            bigrams = self._generate_ngrams(unigrams)
            all_tokens = unigrams + bigrams
            term_counts = Counter(all_tokens)
            temp_doc_data.append(term_counts)   #和词 加 未和的词

        for docid, term_counts in enumerate(temp_doc_data):
            doc_len = sum(term_counts.values())
            self.doc_lengths.append(doc_len)
            for term, tf in term_counts.items():
                self.inverted_index[term].append(Posting(docid, tf))

        self.total_docs = len(self.doc_info)
        if self.total_docs > 0:
            self.avg_doc_len = sum(self.doc_lengths) / self.total_docs

        for term, plist in self.inverted_index.items():
            df = len(plist)
            plist.insert(0, Posting(Posting.special_doc_id, df))

        print(f"[INDEX BUILT] 索引构建完成。")
        print(f"  - 词项总数 (含Bigram): {len(self.inverted_index)}")
        print(f"  - 文档总数: {self.total_docs}")
        print(f"  - 平均文档长度: {self.avg_doc_len:.2f}")

    # <-- 2. 新增：保存索引的方法 -->
    def save_index(self, filepath):
        """将当前搜索引擎的核心数据保存到文件。"""
        print(f"--- 正在保存索引到文件: {filepath} ---")
        index_data = {
            "inverted_index": self.inverted_index,
            "doc_lengths": self.doc_lengths,
            "doc_info": self.doc_info,
            "total_docs": self.total_docs,
            "avg_doc_len": self.avg_doc_len,
        }
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
        print(f"[SUCCESS] 索引已成功保存。")

    # <-- 3. 新增：加载索引的方法 -->
    def load_index(self, filepath):
        """从文件加载索引数据。"""
        if not os.path.exists(filepath):
            return False
        
        print(f"--- 正在从文件加载索引: {filepath} ---")
        with open(filepath, 'rb') as f:
            index_data = pickle.load(f)
        
        self.inverted_index = index_data["inverted_index"]
        self.doc_lengths = index_data["doc_lengths"]
        self.doc_info = index_data["doc_info"]
        self.total_docs = index_data["total_docs"]
        self.avg_doc_len = index_data["avg_doc_len"]
        
        print(f"[SUCCESS] 索引加载完成。")
        print(f"  - 词项总数 (含Bigram): {len(self.inverted_index)}")
        print(f"  - 文档总数: {self.total_docs}")
        return True

    def _calculate_idf(self, df):
        N = self.total_docs
        return math.log(1 + (N - df + 0.5) / (df + 0.5))

    def search(self, query):
        if not self.inverted_index:
            print("索引为空，无法执行搜索。")
            return [], []

        unigrams_query = [self._filter_text(w) for w in jieba.lcut_for_search(query) if self._filter_text(w)]
        bigrams_query = self._generate_ngrams(unigrams_query)
        query_terms = unigrams_query + bigrams_query
        
        if not query_terms:
            return [], []

        scores = defaultdict(float)
        
        for term, q_tf in Counter(query_terms).items():
            if term not in self.inverted_index:
                continue

            plist = self.inverted_index[term]
            df = plist[0].tf
            idf = self._calculate_idf(df)
            
            for posting in plist[1:]:
                docid, tf = posting.docid, posting.tf
                doc_len = self.doc_lengths[docid]
                K = self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
                tf_score = (tf * (self.k1 + 1)) / (tf + K)
                scores[docid] += idf * tf_score
        
        if not scores:
            return [], query_terms
            
        sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        results = []
        for docid, _ in sorted_docs:
            results.append({
                "title": self.doc_info[docid]["title"],
                "url": self.doc_info[docid]["url"]
            })
        
        return results, unigrams_query

JSON_FOLDER = 'D:\\CursorCode\\__test__\\wordsegment'
INDEX_FILE_PATH = 'D:\CursorCode\__test__\search_engine.index.pkl'  # 定义索引文件的路径和名称


print("--- 正在初始化搜索引擎 (BM25 + Bigram)... ---")
engine = SearchEngine(k1=1.5, b=0.75)

# 尝试加载索引，如果失败，则构建新索引并保存
if not engine.load_index(INDEX_FILE_PATH):
    print(f"未找到索引文件 '{INDEX_FILE_PATH}'。")
    print("将从JSON文件开始构建新索引，这可能需要一些时间...")
    engine.build_index_from_json(JSON_FOLDER)
    engine.save_index(INDEX_FILE_PATH)

print("--- 搜索引擎初始化完成，准备接收查询。 ---")

def evaluate(query: str) -> list[str]:
    """
    评测函数，接收一个查询，返回排序后的URL列表。
    """
    if not query:
        return []
    
    results_with_details, _ = engine.search(query)
    urls = [result['url'] for result in results_with_details]
    return urls

if __name__ == '__main__':
    test_query = "搜索引擎的工作原理"
    print(f"\n执行查询: '{test_query}'")
    url_list = evaluate(test_query)
    
    if url_list:
        print("查询结果 (URL列表):")
        for i, url in enumerate(url_list[:10]): # 最多显示前10个结果
            print(f"{i+1}. {url}")
    else:
        print("没有找到相关结果。")