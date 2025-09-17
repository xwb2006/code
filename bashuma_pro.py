import heapq
import copy

'''全局最优，通过记录所有的 f 值'''
# 目标状态
goal_state = [
    [1, 2, 3],
    [8, 0, 4],
    [7, 6, 5]
]

# 启发函数1，曼哈顿距离
def h_fun(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value != 0:
                # 与目标状态比对
                for x in range(3):
                    for y in range(3):
                        if goal_state[x][y] == value:
                            distance += abs(i - x) + abs(j - y)
    return distance

# 启发函数2，不在位数码数
def h_fun1(state): 
    cnt = 0
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value != 0:
                if goal_state[i][j] != value:
                    cnt += 1
    return cnt

# 下一步状态
def get_next_states(state):
    next = []
    #先获取 0 位置
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                empty_i, empty_j = i, j
                break
    dirs = [(-1,0),(1,0),(0,-1),(0,1)]
    for di, dj in dirs:
        ni, nj = empty_i + di, empty_j + dj
        if 0<=ni<3 and 0<=nj<3:
            new_state = copy.deepcopy(state)
            new_state[empty_i][empty_j], new_state[ni][nj] = new_state[ni][nj], new_state[empty_i][empty_j]
            next.append(new_state)
    return next

# 状态转字符串（用于打印）
def state_to_str(state):
    return '\n'.join([' '.join([' ' if x==0 else str(x) for x in row]) for row in state])

# A*算法主函数
def solve_puzzle(initial_state):
    open_heap = []  # 优先队列：(f, g, state, parent)
    visited = {}    # 记录最小g值的状态
    
    # 初始化根节点
    initial_g = 0
    initial_h = h_fun1(initial_state)
    heapq.heappush(open_heap, (initial_g + initial_h, initial_g, initial_state))
    visited[tuple(map(tuple, initial_state))] = initial_g
    
    step = 0
    while open_heap:
        # 打印当前步骤所有候选状态
        print(f"\n{'─'*20} 步骤 {step} ────────────────────────")
        current_nodes = []
        temp_heap = []
        while open_heap:
            f, g, state = heapq.heappop(open_heap)
            current_nodes.append((f, g, state))
            temp_heap.append((f, g, state))
        # 恢复优先队列并按f排序
        for item in temp_heap:
            heapq.heappush(open_heap, item)
            current_nodes.sort(key=lambda x: (x[0], x[1]))
        
        # 打印所有候选状态
        for idx, (f, g, state) in enumerate(current_nodes):
            prefix = f" S{step}_{idx}({f}={g}+{f-g})"
            print(prefix)
            print(state_to_str(state))
            print()
        
        # 取出当前扩展节点（f最小）
        current_f, current_g, current_state = heapq.heappop(open_heap)
        if current_state == goal_state:
            print("\n★★★ 找到目标状态 ★★★")
            return
        
        # 生成子节点
        next_states = get_next_states(current_state)
        for next_state in next_states:
            next_g = step + 1
            next_h = h_fun1(next_state)
            next_f = next_g + next_h
            state_key = tuple(map(tuple, next_state))
            
            # 只保留更优的g值
            if state_key not in visited or next_g < visited[state_key]:
                visited[state_key] = next_g
                heapq.heappush(open_heap, (next_f, next_g, next_state))
        
        step += 1

# 测试（与原代码初始状态一致）
if __name__ == "__main__":
    initial_state = [
        [2, 8, 3],
        [1, 6, 4],
        [7, 0, 5]
    ]
    solve_puzzle(initial_state)