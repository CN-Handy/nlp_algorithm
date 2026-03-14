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


def social_network_queries():
    """社交网络查询"""
    # 查找最有影响力的用户（最多朋友）
    query = """
    MATCH (u:User)-[r:FRIENDS_WITH]-()
    RETURN u.name as user, COUNT(r) as friend_count
    ORDER BY friend_count DESC
    LIMIT 5
    """
    result = graph.run(query)
    print("最有影响力的用户:")
    for record in result:
        print(f"{record['user']}: {record['friend_count']} 个朋友")

    # 查找共同朋友
    query = """
    MATCH (u1:User {name: 'User_0'})-[:FRIENDS_WITH]-(mutual:User)-[:FRIENDS_WITH]-(u2:User {name: 'User_1'})
    RETURN mutual.name as mutual_friend
    """
    result = graph.run(query)
    mutual_friends = [record['mutual_friend'] for record in result]
    print(f"User_0 和 User_1 的共同朋友: {mutual_friends}")

clear_database()
social_network_example()
social_network_queries()