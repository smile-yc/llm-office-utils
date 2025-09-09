
# 深度优先搜索（DFS）递归实现
def dfs_recursive(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start)
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    return visited

# 深度优先搜索（DFS）非递归实现
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            print(vertex)
            visited.add(vertex)
            stack.extend(reversed(graph.get(vertex, [])))
    return visited

# 示例用法
if __name__ == "__main__":
    # 定义一个简单的无向图
    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        'D': ['B'],
        'E': ['B', 'F'],
        'F': ['C', 'E']
    }
    print("递归DFS遍历:")
    dfs_recursive(graph, 'A')
    print("\n非递归DFS遍历:")
    dfs_iterative(graph, 'A')
