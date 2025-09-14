from flask import Flask, render_template, request

from search_pro import engine # <--- 1. 导入 engine
app = Flask(__name__)

# 定义每页显示的条目数
RESULTS_PER_PAGE = 15

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods = ['GET'])
def query():
    key = request.args.get('key')
    page = request.args.get('page', 1, type=int) # 新增：获取page参数，若无则默认为1
    results = []
    pagination = {} # 创建一个空字典，用于存放分页信息
    # Implement your search engine here.
    # Generate a list of search results.
    if key and key.strip():
        # 调用 evaluate 函数
        raw_res, key_tokens_from_search = engine.search(key)
        total_results = len(raw_res)
        # --- 2. 新增：计算分页逻辑 ---
        # 计算总页数
        total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        
        # 根据页码对完整结果进行切片
        start_index = (page - 1) * RESULTS_PER_PAGE
        end_index = start_index + RESULTS_PER_PAGE
        results_for_this_page = raw_res[start_index:end_index]

        # 将所有分页信息打包，方便传给前端
        pagination = {
            'page': page,
            'total_results':total_results,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1,
            'next_num': page + 1,
        }
        for result in results_for_this_page:
            # --- 处理标题高亮 (保持不变) ---
            highlighted_title = result['title']
            for token in key_tokens_from_search:
                if token in highlighted_title:
                    highlighted_title = highlighted_title.replace(token, f'<span class="highlight">{token}</span>')
            
            # --- 新增对摘要的高亮处理 ---
            highlighted_snippet = result.get('snippet', '')
            for token in key_tokens_from_search:
                if token in highlighted_snippet:
                    highlighted_snippet = highlighted_snippet.replace(token, f'<span class="highlight">{token}</span>')

            # 在 result 字典中添加处理后的标题和摘要
            result['highlighted_title'] = highlighted_title
            result['highlighted_snippet'] = highlighted_snippet # 新增这一行
            results.append(result)

    return render_template('res.html', key=key, results=results,pagination=pagination)

app.run(host='0.0.0.0', port=12345, debug=True)
