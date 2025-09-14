import time
import matplotlib.pyplot as plt
import numpy as np

def append_and_reverse(n):
    mylist = []
    start_time = time.time()
    for i in range(1, n + 1):
        mylist.append(i)
    mylist.sort(reverse=True)
    end_time = time.time()
    return end_time - start_time

def insert_at_position(n):
    mylist = []
    start_time = time.time()
    for i in range(1, n + 1):
        mylist.insert(1, i)
    end_time = time.time()
    return end_time - start_time

# 生成不同的n值，这里以1000到1000000，步长100000为例
n_values = np.arange(100, 10000, 100)
append_times = []
insert_times = []

for n in n_values:
    append_times.append(append_and_reverse(n))
    insert_times.append(insert_at_position(n))

plt.figure(figsize=(10, 6))
plt.plot(n_values, append_times, 'o-', label='Append + Reverse')
plt.plot(n_values, insert_times, 's-', label='Insert at Position 1')
plt.xlabel('n (Number of Elements)')
plt.ylabel('Time (seconds)')
plt.title('Time Comparison: Append + Reverse vs Insert at Position 1')
plt.legend()
plt.grid(True)
plt.show()