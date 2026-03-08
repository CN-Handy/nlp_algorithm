import networkx as nx # 图创建、操作、图算法、图可视化
import matplotlib.pyplot as plt
import numpy as np


# 1. 加载Karate Club数据集
G = nx.karate_club_graph()
print(f"数据集信息: {G}")
print(f"节点数量: {G.number_of_nodes()}")
print(f"边数量: {G.number_of_edges()}")

# 2. 计算PageRank值
# pagerank 图中所有节点的重要性
pagerank = nx.pagerank(G, alpha=0.85)  # alpha是阻尼系数，通常设为0.85

# 3. 提取PageRank值用于节点大小
node_sizes = [3000 * pagerank[node] for node in G.nodes()]

# 4. 找出最重要的节点（PageRank值最高的节点）
top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
print("\nPageRank值最高的5个节点:")
for node, score in top_nodes:
    print(f"节点 {node}: PageRank值 = {score:.4f}")

# 5. 可视化图形
plt.figure(figsize=(14, 6))

# 子图1: 原始图形布局
plt.subplot(121)
pos = nx.spring_layout(G, seed=42)  # 使用spring布局，固定随机种子以确保可重复性
nx.draw_networkx_nodes(G, pos, node_size=200, node_color='lightblue')
nx.draw_networkx_edges(G, pos, alpha=0.4)
nx.draw_networkx_labels(G, pos, font_size=8)
plt.title("Karate Club Network")
plt.axis('off')

plt.subplot(122)
nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                               node_color=list(pagerank.values()),
                               cmap=plt.cm.plasma)
nx.draw_networkx_edges(G, pos, alpha=0.3)
nx.draw_networkx_labels(G, pos, font_size=8)

# 添加颜色条
plt.colorbar(nodes, label='PageRank Value')
plt.axis('off')

plt.tight_layout()
plt.show()

# 6. 额外分析：展示PageRank值的分布
plt.figure(figsize=(10, 5))
values = list(pagerank.values())
plt.hist(values, bins=15, alpha=0.7, color='skyblue', edgecolor='black')
plt.xlabel('PageRank Value')
plt.ylabel('频率')
plt.title('PageRank')
plt.grid(axis='y', alpha=0.3)
plt.show()

# 7. 展示节点度中心性与PageRank的关系
degrees = dict(G.degree())
degree_values = [degrees[node] for node in G.nodes()]
pagerank_values = [pagerank[node] for node in G.nodes()]

plt.figure(figsize=(10, 6))
plt.scatter(degree_values, pagerank_values, alpha=0.7)
plt.xlabel('节点度')
plt.ylabel('PageRank Value')

# 添加趋势线
z = np.polyfit(degree_values, pagerank_values, 1)
p = np.poly1d(z)
plt.plot(degree_values, p(degree_values), "r--", alpha=0.8)

# 标记最重要的节点
for node, _ in top_nodes[:3]:
    plt.annotate(str(node), (degrees[node], pagerank[node]),
                 xytext=(5, 5), textcoords='offset points', fontweight='bold')

plt.grid(alpha=0.3)
plt.show()

# 8. 输出网络的基本统计信息
print("\n网络基本统计信息:")
print(f"平均度: {sum(degree for node, degree in G.degree()) / G.number_of_nodes():.2f}")
print(f"网络直径: {nx.diameter(G)}")
print(f"平均聚类系数: {nx.average_clustering(G):.3f}")
print(f"平均最短路径长度: {nx.average_shortest_path_length(G):.3f}")