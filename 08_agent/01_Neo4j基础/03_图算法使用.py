from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
from py2neo.data import walk

# 连接 Neo4j 数据库
graph = Graph('bolt://localhost:7687')


def clear_database():
    """清空数据库"""
    graph.delete_all()

def social_network_example():
    """社交网络分析"""
    # 创建社交网络数据
    users = []
    for i in range(10):
        user = Node("User",
                    name=f"User_{i}",
                    age=20 + i,
                    interests=["music", "sports", "tech"][i % 3])
        users.append(user)

    # 创建关系 - 模拟社交网络
    tx = graph.begin()
    for user in users:
        tx.create(user)

    # 创建随机关系
    import random
    relationships = []
    for i in range(20):
        user1 = random.choice(users)
        user2 = random.choice(users)
        if user1 != user2:
            rel = Relationship(user1, "FRIENDS_WITH", user2,
                               strength=random.randint(1, 10))
            relationships.append(rel)
            tx.create(rel)

    graph.commit(tx)
    print("社交网络数据创建完成")

def graph_algorithms():
    """图算法应用"""

    # 最短路径
    query = """
    MATCH (start:User {name: 'User_0'}), (end:User {name: 'User_9'})
    MATCH path = shortestPath((start)-[:FRIENDS_WITH*]-(end))
    RETURN [node in nodes(path) | node.name] as path,
           length(path) as degrees_of_separation
    """
    result = graph.run(query)
    for record in result:
        print(f"最短路径: {' -> '.join(record['path'])}")
        print(f"分离度数: {record['degrees_of_separation']}")

    # 社区检测 (使用 Neo4j 的图算法库)
    query = """
    CALL gds.graph.project(
        'social-network',
        'User',
        'FRIENDS_WITH'
    )
    """
    # 注意：需要安装 Neo4j Graph Data Science 库
    try:
        graph.run(query)

        # Louvain 社区检测
        community_query = """
        CALL gds.louvain.stream('social-network')
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).name as user, communityId
        ORDER BY communityId, user
        """
        result = graph.run(community_query)
        communities = {}
        for record in result:
            community = record['communityId']
            if community not in communities:
                communities[community] = []
            communities[community].append(record['user'])

        print("检测到的社区:")
        for community, members in communities.items():
            print(f"社区 {community}: {members}")
    except Exception as e:
        print(f"图算法需要 Neo4j GDS 库: {e}")

def pagerank_example():
    """PageRank 算法示例"""
    query = """
    CALL gds.graph.project(
        'pagerank-graph',
        'User',
        'FRIENDS_WITH'
    )
    """
    try:
        graph.run(query)

        pagerank_query = """
        CALL gds.pageRank.stream('pagerank-graph')
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).name as user, score
        ORDER BY score DESC
        LIMIT 5
        """
        result = graph.run(pagerank_query)
        print("PageRank 排名前5的用户:")
        for record in result:
            print(f"{record['user']}: {record['score']:.4f}")
    except Exception as e:
        print(f"PageRank 需要 Neo4j GDS 库: {e}")


clear_database()
graph_algorithms()
social_network_example()
pagerank_example()