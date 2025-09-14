# 元组替代Posting对象 + 按需加载正文生成摘要
import os
import json
import jieba
import re
import math
import pickle
from collections import defaultdict, Counter

class SearchEngine:
    def __init__(self, k1=1.5, b=0.75):
        self.inverted_index = defaultdict(list) # 倒排索引
        self.doc_lengths = []   #存储每个文档的长度
        self.doc_info = {} # 存储每个文档的元数据，标题、URL等，通过docid索引
        self.total_docs = 0
        self.avg_doc_len = 0.0
        # k1: 控制词频饱和度，值越高，词频对分数的影响越大，但增长会放缓。
        self.k1 = k1
        # b: 控制文档长度归一化的程度，b=0.75是标准值，b=1表示完全归一化，b=0则不考虑文档长度
        self.b = b
        # 记录原始JSON文件的目录，用于在搜索时按需加载文档正文以生成摘要
        self.json_dir = None

    def _filter_text(self, text):
        """一个简单的文本清洗函数，只保留中文字符、字母和数字。"""
        pattern = re.compile(r'[^一-龥a-zA-Z0-9]')
        return pattern.sub('', text).strip()

    @staticmethod
    def _generate_ngrams(tokens, n=2):
        """
        生成2-grams(二元语法），相邻的两个词组成词组
        """
        ngrams = zip(*[tokens[i:] for i in range(n)])
        return ["".join(ngram) for ngram in ngrams]

    def build_index_from_json(self, json_dir):
        """
        从JSON文件目录构建倒排索引。
        为了优化内存，此函数只处理文本和词频，暂时不将全文加载到内存中。
        """
        self.json_dir = json_dir
        if not os.path.exists(json_dir):
            print(f"[ERROR] 目录不存在: {json_dir}")
            return

        json_files = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')])

        print(f"--- 正在构建索引 ---")

        temp_doc_data = []
        for docid, filename in enumerate(json_files):
            file_path = os.path.join(json_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                continue

            self.doc_info[docid] = {
                "title": data.get("page_title", "无标题"),
                "url": data.get("source_url", "未知URL"),
                "filename": filename # 存储原始文件名，用于后续按需加载
            }
            
            title = data.get("page_title", "")
            body = data.get("full_body_text", "")
            # 通过将标题内容重复3次，提高了标题中词元的词频(tf)，从而提升其在搜索结果中的权重。
            full_text = (title + " ") * 3 + body

            # 核心:结合unigram和bigram建立索引
            # unigram保证了召回率，bigram则通过词组匹配提高了准确率。
            unigrams = [self._filter_text(w) for w in jieba.lcut_for_search(full_text) if self._filter_text(w)]
            bigrams = self._generate_ngrams(unigrams)
            all_tokens = unigrams + bigrams
            term_counts = Counter(all_tokens)
            temp_doc_data.append(term_counts)

        # 第二遍遍历，构建的倒排索引
        for docid, term_counts in enumerate(temp_doc_data):
            doc_len = sum(term_counts.values())
            self.doc_lengths.append(doc_len)
            for term, tf in term_counts.items():
                # 使用元组 (docid, tf) 代替专门的Posting对象，显著节省内存。
                self.inverted_index[term].append((docid, tf))

        self.total_docs = len(self.doc_info)
        if self.total_docs > 0:
            self.avg_doc_len = sum(self.doc_lengths) / self.total_docs

        # 将文档频率(DF)存储在倒排列表的头部 
        # 这样做可以在搜索时快速获取DF，而无需再次计算或查询其他数据结构。
        for term, plist in self.inverted_index.items():
            df = len(plist)
            # 使用一个特殊的docid（如-1）来标记是存储DF的。
            plist.insert(0, (-1, df))

        print(f"[INDEX BUILT] 索引构建完成。")

    def save_index(self, filepath):
        """将搜索引擎的核心数据（包括索引和元数据）序列化到文件中。"""
        print(f"--- 正在保存索引到文件: {filepath} ---")
        index_data = {
            "inverted_index": self.inverted_index,
            "doc_lengths": self.doc_lengths,
            "doc_info": self.doc_info,
            "total_docs": self.total_docs,
            "avg_doc_len": self.avg_doc_len,
            "json_dir": self.json_dir # 保存json目录路径，以便加载后能找到原文
        }
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
        print(f"[SUCCESS] 索引已成功保存。")

    def load_index(self, filepath):
        """从文件反序列化索引数据，重建搜索引擎状态。"""
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
        # 使用 .get() 方法安全地获取json_dir，这样即使加载旧版没有该字段的索引文件也不会报错。
        self.json_dir = index_data.get("json_dir")
        
        print(f"[SUCCESS] 索引加载完成。")
        return True

    def _calculate_idf(self, df):
        """
        计算逆文档频率 (IDF)。
        采用BM25的概率IDF公式，能更好地处理极端情况（如一个词出现在所有文档中）。
        N: 文档总数
        df: 出现过该词的文档数
        """
        N = self.total_docs
        # +0.5 和 +1 是为了平滑，避免df过大或过小导致log计算结果为负或除零
        return math.log(1 + (N - df + 0.5) / (df + 0.5))

    def search(self, query):
        if not self.inverted_index:
            return [], []

        # 对查询进行与文档相同的处理（分词、bigram），确保查询和索引的格式一致
        unigrams_query = [self._filter_text(w) for w in jieba.lcut_for_search(query) if self._filter_text(w)]
        bigrams_query = self._generate_ngrams(unigrams_query)
        #使用分词 + bigram作为搜索文本
        query_terms = unigrams_query + bigrams_query
        
        # 使用defaultdict(float)来累加每个文档的BM25分数
        scores = defaultdict(float)
        
        for term, q_tf in Counter(query_terms).items():
            if term not in self.inverted_index:
                continue

            plist = self.inverted_index[term]
            # 直接从倒排列表的头部元组解包，快速获取DF
            _, df = plist[0] 
            idf = self._calculate_idf(df)
            
            # 遍历该词元对应的所有文档（从索引1开始，跳过头部的DF信息）
            for posting in plist[1:]:
                docid, tf = posting # 从元组解包出文档ID和词频
                doc_len = self.doc_lengths[docid]
                
                # BM25核心公式
                # 计算文档长度归一项 K
                K = self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
                # 计算词频饱和度项
                tf_score = (tf * (self.k1 + 1)) / (tf + K)
                # 累加该词元对文档的总分
                scores[docid] += idf * tf_score
        
        if not scores:
            return [], query_terms
            
        # 根据BM25分数对文档进行降序排序
        sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        results = []
        # 只为Top N结果生成摘要
        for docid, _ in sorted_docs[:100]:
            doc_meta = self.doc_info[docid]
            snippet = ""
            # 按需加载原文,避免了在初始化时将所有文档的全文加载到内存中。
            if self.json_dir and doc_meta.get("filename"):
                try:
                    file_path = os.path.join(self.json_dir, doc_meta["filename"])
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        full_text = data.get("full_body_text", "")
                        snippet = full_text[:100]
                        if len(full_text) > 100:
                            snippet += "..."
                except Exception as e:
                    snippet = "[摘要加载失败]"

            results.append({
                "title": doc_meta["title"],
                "url": doc_meta["url"],
                "snippet": snippet
            })
        
        return results, query_terms

# --- 主程序逻辑 ---
JSON_FOLDER = 'D:\\CursorCode\\__test__\\wordsegment'
INDEX_FILE_PATH = 'D:\\CursorCode\\WEBUI\\search_pro.index.pkl'

print("--- 正在初始化搜索引擎 (内存优化版)... ---")
engine = SearchEngine(k1=1.8, b=0.6)

# 启动时，首先尝试从文件加载已构建好的索引，以加快启动速度
if not engine.load_index(INDEX_FILE_PATH):
    # 如果索引文件不存在，则现场从JSON文件构建索引，并保存以备下次使用
    print(f"未找到索引文件 '{INDEX_FILE_PATH}'。")
    engine.build_index_from_json(JSON_FOLDER)
    engine.save_index(INDEX_FILE_PATH)

print("--- 搜索引擎初始化完成，准备接收查询。 ---")