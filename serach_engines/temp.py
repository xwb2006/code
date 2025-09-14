# 从一个JSON文件夹中读取数据，构建索引
'''基于 BM25 算法,标题权重,k=1.8, evaluate,score:0.8167'''
import os,json,jieba,re,math
from collections import defaultdict

# ---------- Posting 类 (无改动) ----------
class Posting(object):
    """
    Posting 类用于表示倒排索引中的一个条目。
    special_doc_id = -1 用于存储词项的额外信息，如文档频率(df)。
    """
    special_doc_id = -1
    def __init__(self, docid, tf=0):
        self.docid = docid
        self.tf = tf # 词频 (term frequency)

    def __repr__(self):
        return f"<docid: {self.docid}, tf: {self.tf}>"

# ---------- 搜索引擎类 (优化版) ----------
class SearchEngine:
    # 新增 title_weight 参数，用于控制标题字段的权重
    def __init__(self, json_dir="word_segments", k1=1.5, b=0.75, title_weight=2.0):

        self.json_dir = json_dir
        self.inverted_index = defaultdict(list)
        self.doc_lengths = []
        # self.doc_info 中新增一个字段 'title_terms' 用于存放标题分词结果
        self.doc_info = {}     # 格式: {docid: {"title": ..., "url": ..., "title_terms": set(...)}}
        self.total_docs = 0
        self.avg_doc_len = 0.0
        
        # BM25 参数
        self.k1 = k1 
        self.b = b
        # 新增的权重参数
        self.title_weight = title_weight
        
        self._load_from_json_files()

    def _filter_text(self, text):
        """
        过滤字符串，只保留中文、字母和数字。
        """
        pattern = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9]')
        return pattern.sub('', text).strip().lower() # 增加 .lower() 统一转为小写，增强鲁棒性

    def _load_from_json_files(self):
        """
        从指定的JSON文件夹加载数据，构建倒排索引，并计算BM25所需的全局统计信息。
        """
        if not os.path.exists(self.json_dir):
            print(f"[ERROR] 目录不存在: {self.json_dir}")
            return

        json_files = sorted([f for f in os.listdir(self.json_dir) if f.endswith('.json')])
        if not json_files:
            print(f"[ERROR] 目录 {self.json_dir} 中没有找到JSON文件。")
            return
            
        print(f"--- 正在从 {len(json_files)} 个JSON文件中加载并构建索引 ---")

        for docid, filename in enumerate(json_files):
            file_path = os.path.join(self.json_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"[LOAD ERROR] 读取或解析 {filename} 失败: {e}")
                self.doc_lengths.append(0)
                continue

            title = data.get("page_title", "无标题")
            
            # --- 新增逻辑：对标题进行分词并存储 ---
            # 使用 jieba 对标题进行分词
            raw_title_words = jieba.lcut(title)
            # 对分词结果进行过滤和清洗，并存储为 set 以便快速查找
            title_terms_set = {self._filter_text(w) for w in raw_title_words if self._filter_text(w)}

            self.doc_info[docid] = {
                "title": title,
                "url": data.get("source_url", "未知URL"),
                "title_terms": title_terms_set # 存储处理后的标题词集合
            }

            terms_with_tf = data.get("segmented_words", [])
            doc_len = sum(item[1] for item in terms_with_tf)
            self.doc_lengths.append(doc_len)
            
            for term, tf in terms_with_tf:
                # 对来自 JSON 的 term 也进行一次过滤，确保一致性
                clean_term = self._filter_text(term)
                if clean_term:
                    self.inverted_index[clean_term].append(Posting(docid, tf))
        
        self.total_docs = len(self.doc_info)
        if self.total_docs > 0:
            self.avg_doc_len = sum(self.doc_lengths) / self.total_docs

        for term, plist in self.inverted_index.items():
            df = len(plist)
            plist.insert(0, Posting(Posting.special_doc_id, df))

        print(f"[INDEX BUILT] 索引构建完成。")
        print(f"  - 词项总数 (Total Terms): {len(self.inverted_index)}")
        print(f"  - 文档总数 (Total Docs): {self.total_docs}")
        print(f"  - 平均文档长度 (Avg Doc Length): {self.avg_doc_len:.2f}")

    def _calculate_idf(self, df):
        """
        计算词项的IDF值。(无改动)
        """
        N = self.total_docs
        return math.log(1 + (N - df + 0.5) / (df + 0.5))

    def search(self, query):
        """
        使用带有字段权重的 BM25 算法执行搜索查询。
        """
        if not self.inverted_index:
            print("索引为空，无法执行搜索。")
            return []

        raw_words = jieba.lcut(query)
        query_terms = [self._filter_text(w) for w in raw_words if self._filter_text(w)]
        
        if not query_terms:
            return []

        scores = defaultdict(float)
        
        for term in query_terms:
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
                
                # --- 核心改动：应用字段权重 ---
                # 检查当前词项是否也存在于该文档的标题词集合中
                weight = 2.0
                if term in self.doc_info[docid]['title_terms']:
                    weight = self.title_weight # 如果是标题词，则使用更高的权重

                scores[docid] += idf * tf_score * weight
        
        if not scores:
            return []
            
        sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        results_urls = [self.doc_info[docid]["url"] for docid, score in sorted_docs]
        
        return results_urls

# ---------------- 评测客户端接口 (保持不变) ----------------

# 1. 设置包含JSON文件的文件夹路径
# 注意：请确保 jieba 库已安装 (pip install jieba)
JSON_FOLDER = 'D:\\CursorCode\\__test__\\wordsegment' 

# 2. 初始化全局搜索引擎实例
print("--- 正在初始化搜索引擎 (BM25模型, 优化版)，请稍候... ---")
# 初始化时可以传入自定义的 title_weight
engine = SearchEngine(json_dir=JSON_FOLDER, title_weight=2.0,k1=1.8,b=0.6) 
print("--- 搜索引擎初始化完成，准备接收查询。 ---")

def evaluate(query: str) -> list[str]:
    """
    评测函数，接收一个查询，返回排序后的URL列表。
    """
    if not query:
        return []
    return engine.search(query)