# 从一个JSON文件夹中读取数据，构建索引,search——pro
'''（原始版）基于 BM25 算法的 evaluate,score:0.81'''

import os,json,jieba,re,math
from collections import defaultdict

# ---------- Posting 类  ----------
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

# ---------- 搜索引擎类 (采用BM25模型重构并优化) ----------
class SearchEngine:
    def __init__(self, json_dir="word_segments", k1=1.5, b=0.75):

        self.json_dir = json_dir  #存放JSON分词结果文件的目录
        self.inverted_index = defaultdict(list)
        self.doc_lengths = []  # 使用列表代替字典以优化内存和速度
        self.doc_info = {}     # 存储每个docid对应的URL和标题 {docid: {"title": ..., "url": ...}}
        self.total_docs = 0
        self.avg_doc_len = 0.0
        
        # BM25 参数
        '''控制文档长度归一化的强度。值为 0.0 意味着完全不考虑文档长度，值为 1.0 意味着最大化惩罚。常用值为 0.75。'''
        self.k1 = k1 
        '''BM25算法参数。'''
        self.b = b
        
        self._load_from_json_files()
        

    def _filter_text(self, text):
        """
        过滤字符串，只保留中文、字母和数字。
        """
        # [修正] 将不完整的Unicode转义 \u4e--\u9fa5 修改为正确的范围 \u4e00-\u9fa5
        pattern = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9]')
        return pattern.sub('', text).strip()

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

            # 【修改点】存储文档元数据时，额外增加 full_body_text
            self.doc_info[docid] = {
                "title": data.get("page_title", "无标题"),
                "url": data.get("source_url", "未知URL"),
                "full_body_text": data.get("full_body_text", "") # 新增这一行
            }
            # ... (后续填充倒排索引的逻辑保持不变) ...
            terms_with_tf = data.get("segmented_words", [])
            doc_len = sum(item[1] for item in terms_with_tf)
            self.doc_lengths.append(doc_len)
            for term, tf in terms_with_tf:
                self.inverted_index[term].append(Posting(docid, tf))

        # ... (后续计算全局统计信息的逻辑保持不变) ...
        self.total_docs = len(self.doc_info)
        if self.total_docs > 0:
            self.avg_doc_len = sum(self.doc_lengths) / self.total_docs
        for term, plist in self.inverted_index.items():
            df = len(plist)
            plist.insert(0, Posting(Posting.special_doc_id, df))

        print(f"[INDEX BUILT] 索引构建完成。")
        print(f"  - 词项总数 (Total Terms): {len(self.inverted_index)}")
        print(f"  - 文档总数 (Total Docs): {self.total_docs}")
  
    def _calculate_idf(self, df):
        """
        计算词项的IDF值。
        采用BM25推荐的平滑公式，避免df为N时log(1)为0以及df很大时出现负值的情况。
        """
        N = self.total_docs
        # Okapi BM25 IDF formula
        return math.log(1 + (N - df + 0.5) / (df + 0.5))

    def search(self, query):
        """
        使用 BM25 算法执行搜索查询，返回排序好的URL列表。
        :param query: 用户输入的查询字符串。
        :return: 一个按相关性排序的所有URL的列表。
        """
        if not self.inverted_index:
            print("索引为空，无法执行搜索。")
            return [],[]

        # 查询预处理：对查询语句分词并过滤
        raw_words = jieba.lcut_for_search(query)
        query_terms = [self._filter_text(w) for w in raw_words if self._filter_text(w)]
        
        if not query_terms:
            return [],[]

        scores = defaultdict(float)
        
        # 遍历查询中的每个词项 (q_i)，计算并累加其对每个相关文档的BM25得分
        for term in query_terms:
            if term not in self.inverted_index:
                continue

            plist = self.inverted_index[term]
            df = plist[0].tf # 从预存的特殊Posting中获取df
            # 计算当前查询词项的IDF值
            idf = self._calculate_idf(df)
            # 遍历该词项的倒排列表 (只包含实际文档)
            for posting in plist[1:]:
                docid, tf = posting.docid, posting.tf
                doc_len = self.doc_lengths[docid]
                # --- BM25核心评分公式 ---
                # 1. IDF部分: 由idf变量代表
                # 2. 词频饱和度部分: (tf * (k1 + 1)) / (tf + K)
                # 3. 文档长度归一化部分: K = k1 * (1 - b + b * doc_len / avg_doc_len)
                K = self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
                tf_score = (tf * (self.k1 + 1)) / (tf + K)
                # 累加该词项对文档的BM25得分
                scores[docid] += idf * tf_score
        # 3. 对得分进行排序并返回结果
        if not scores:
            return []
        # sorted_docs是一个元组列表 [(docid, score), (docid, score), ...]
        sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        # 从排序好的文档中提取标题和URL，并构造成字典列表, 方便后续美化 UI
        results = []
        for docid, _ in sorted_docs:
            # 【修改点】在构造返回结果时，增加摘要(snippet)
            full_text = self.doc_info[docid]["full_body_text"]
            snippet = full_text[:50]  # 截取前50个字符
            if len(full_text) > 50:
                snippet += "..."  # 如果正文长度超过50，则添加省略号

            results.append({
                "title": self.doc_info[docid]["title"],
                "url": self.doc_info[docid]["url"],
                "snippet": snippet # 截取前50个字符
            })
        return results, query_terms

# ---------------- 评测客户端接口 (与原文件相同) ----------------

# 1. 设置包含JSON文件的文件夹路径
JSON_FOLDER = 'D:\\CursorCode\\__test__\\wordsegment'

# 2. 初始化全局搜索引擎实例
print("--- 正在初始化搜索引擎 (BM25模型, 优化版)，请稍候... ---")
engine = SearchEngine(json_dir=JSON_FOLDER,k1=1.8,b=0.6) 
print("--- 搜索引擎初始化完成，准备接收查询。 ---")

def evaluate(query: str) -> list[str]:
    """
    评测函数，接收一个查询，返回排序后的URL列表。
    这是评测客户端调用的主函数。
    
    :param query: 查询字符串。
    :return: 按相关性排序的URL列表。
    """
    if not query:
        return [],[]
    return engine.search(query)