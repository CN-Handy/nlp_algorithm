# pip install networkx
import networkx as nx # 基础构建图和图分析的库
import matplotlib.pyplot as plt

# 1. 创建一个有向图 (directed graph)
# 你也可以使用 nx.Graph() 创建一个无向图 (undirected graph)
G = nx.DiGraph() # 不是图数据库，创建图和图操作的库

# 2. 添加节点 (add nodes)
G.add_node("A", type="start")
G.add_node("B", type="intermediate")
G.add_node("C", type="intermediate")
G.add_node("D", type="end")
# 一次性添加多个节点
G.add_nodes_from(["E", "F"])

# 3. 添加边 (add edges)
# 添加带有权重的边
G.add_edge("A", "B", weight=5)
G.add_edge("A", "C", weight=2)
G.add_edge("B", "D", weight=8)
G.add_edge("C", "D", weight=10)
G.add_edge("E", "F", weight=1)

# 4. 打印图的信息 (print graph information)
print(f"图中的节点: {G.nodes()}")
print(f"图中的边: {G.edges()}")
print("-" * 20)

# 5. 访问节点和边的属性 (access node and edge attributes)
print(f"节点 'A' 的属性: {G.nodes['A']}")
print(f"边 ('A', 'B') 的权重: {G['A']['B']['weight']}")
print("-" * 20)

# 6. 遍历图中的所有节点和边 (iterate through nodes and edges)
print("所有节点的类型:")
for node, data in G.nodes(data=True):
    print(f"  节点 {node}, 属性: {data}")

print("\n所有边的权重:")
for u, v, data in G.edges(data=True):
    print(f"  边 ({u}, {v}), 权重: {data['weight']}")
print("-" * 20)

# 7. 可视化图 (visualize the graph)
# 设置节点位置布局
pos = nx.spring_layout(G, seed=42)

# 绘制节点
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700)

# 绘制边
nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)

# 绘制节点标签
nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')

# 绘制边标签（权重）
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

plt.title("NetworkX Graph Example")
plt.axis('off')  # 隐藏坐标轴
plt.show()