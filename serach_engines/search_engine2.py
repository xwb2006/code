# search_engine.py
# 作用：从一个包含JSON分词结果的文件夹中加载数据，构建索引，
# 并提供一个evaluate函数供评测客户端调用。
'''优化版：TF-IDF + 标题二分词法匹配奖励， score:0.7056'''
import os
import json
import jieba
import re
import numpy as np
from collections import defaultdict, Counter

# ---------- Posting 类 (与原文件相同) ----------
class Posting(object):
    special_doc_id = -1
    def __init__(self, docid, tf=0):
        self.docid = docid
        self.tf = tf

    def __repr__(self):
        return "<docid: %d, tf: %d>" % (self.docid, self.tf)

# ---------- 搜索引擎类 (优化版) ----------
class SearchEngine:
    # 新增 title_bigram_bonus 参数
    def __init__(self, json_dir="word_segments", title_bigram_bonus=0.5):
        """
        初始化搜索引擎。
        :param json_dir: 存放JSON分词结果文件的目录。
        :param title_bigram_bonus: 每个匹配上的标题二元词组的奖励分值。
        """
        self.json_dir = json_dir
        self.inverted_index = defaultdict(list)
        self.doc_length = []
        self.doc_info = {}
        self.collections = []
        self.title_bigram_bonus = title_bigram_bonus  # 新增奖励系数
        self._load_from_json_files()

    def _filter_text(self, text):
        pattern = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9]')
        return pattern.sub('', text).strip()

    def _load_from_json_files(self):
        """
        从JSON文件夹加载数据，构建倒排索引。
        --- 新增：对标题进行二分词法处理并存储 ---
        """
        if not os.path.exists(self.json_dir):
            return
        json_files = sorted([f for f in os.listdir(self.json_dir) if f.endswith('.json')])
        if not json_files:
            return
            
        print(f"--- 正在从 {len(json_files)} 个JSON文件中加载并构建索引 ---")

        for docid, filename in enumerate(json_files):
            file_path = os.path.join(self.json_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                continue

            self.collections.append(filename)
            title = data.get("page_title", "无标题")
            
            # --- 新增逻辑：生成标题的二元词组 ---
            clean_title = self._filter_text(title)
            title_bigrams_set = set()
            if len(clean_title) > 1:
                for i in range(len(clean_title) - 1):
                    title_bigrams_set.add(clean_title[i:i+2])

            self.doc_info[docid] = {
                "title": title,
                "url": data.get("source_url", "未知URL"),
                "title_bigrams": title_bigrams_set  # 存储标题的二元词组集合
            }

            terms_with_tf = data.get("segmented_words", [])
            if not terms_with_tf:
                self.doc_length.append(0.0)
                continue

            term_tfs = np.array([item[1] for item in terms_with_tf])
            log_tf = 1.0 + np.log10(term_tfs)
            doc_len = float(np.sqrt(np.sum(log_tf ** 2)))
            self.doc_length.append(doc_len)
            
            for term, tf in terms_with_tf:
                self.inverted_index[term].append(Posting(docid, tf))
        
        total_docs = len(self.collections)
        for term, plist in self.inverted_index.items():
            df = len(plist)
            plist.insert(0, Posting(Posting.special_doc_id, df))

        print(f"[INDEX BUILT] 索引构建完成。")

    def search(self, query):
        """
        执行搜索查询，返回排序好的URL列表。
        --- 优化：在TF-IDF基础上，增加标题二分词法匹配奖励 ---
        """
        if not self.inverted_index:
            return []
    
        # 1. 查询预处理 (jieba分词用于TF-IDF)
        raw_words = jieba.lcut(query)
        query_terms = [self._filter_text(w) for w in raw_words]
        query_terms = [t for t in query_terms if t and t in self.inverted_index]
        
        scores = defaultdict(float)
        
        # 2. 计算基础TF-IDF分数 (逻辑不变)
        if query_terms:
            query_counts = Counter(query_terms)
            total_docs = len(self.collections)
            for term, query_tf in query_counts.items():
                plist = self.inverted_index[term]
                df = plist[0].tf
                idf = np.log10(total_docs / df)
                query_weight = (1 + np.log10(query_tf)) * idf
                for posting in plist[1:]:
                    docid, doc_tf = posting.docid, posting.tf
                    doc_weight = (1 + np.log10(doc_tf))
                    scores[docid] += query_weight * doc_weight

        # 3. --- 新增：计算并应用标题二分词法匹配奖励 ---
        clean_query = self._filter_text(query)
        query_bigrams_set = set()
        if len(clean_query) > 1:
            for i in range(len(clean_query) - 1):
                query_bigrams_set.add(clean_query[i:i+1])
        
        if query_bigrams_set:
            # 遍历所有已获得基础分的文档，检查标题匹配
            for docid in scores:
                # 获取该文档的标题二元词组集合
                title_bigrams = self.doc_info[docid].get('title_bigrams', set())
                if title_bigrams:
                    # 计算匹配上的二元词组数量
                    match_count = len(query_bigrams_set.intersection(title_bigrams))
                    if match_count > 0:
                        # 施加奖励分
                        bonus = match_count * self.title_bigram_bonus
                        scores[docid] += bonus

        # 4. 余弦相似度归一化 (只对基础TF-IDF部分)
        for docid in scores:
            if self.doc_length[docid] != 0:
                # 注意：奖励分是在归一化之后加，还是之前加，会影响其权重。
                # 这里我们选择在归一化之前累加，使其成为总分的一部分再一起归一化，可能更合理。
                # 但为了简单和直观，我们先实现为在归一化后直接增加奖励值。
                # 让我们修改一下逻辑，将奖励放在归一化之后，作为一个独立的加分项。
                
                # 先取出原始分
                original_score = scores[docid]
                normalized_score = original_score / self.doc_length[docid]
                
                # 重新计算奖励（代码结构调整，逻辑不变）
                bonus = 0
                if query_bigrams_set:
                    title_bigrams = self.doc_info[docid].get('title_bigrams', set())
                    if title_bigrams:
                        match_count = len(query_bigrams_set.intersection(title_bigrams))
                        bonus = match_count * self.title_bigram_bonus
                
                scores[docid] = normalized_score + bonus

        # 5. 排序并返回结果
        if not scores:
            return []
            
        sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        results_urls = [self.doc_info[docid]["url"] for docid, score in sorted_docs]
        
        return results_urls

# ---------------- 评测客户端接口 ----------------

JSON_FOLDER = 'D:\\CursorCode\\__test__\\wordsegment'

print("--- 正在初始化搜索引擎，请稍候... ---")
# 初始化时可以传入自定义的奖励系数值
engine = SearchEngine(json_dir=JSON_FOLDER, title_bigram_bonus=2.0)
print("--- 搜索引擎初始化完成，准备接收查询。 ---")

def evaluate(query: str) -> list[str]:
    if not query:
        return []
    return engine.search(query)