from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
from py2neo.data import walk

# neo4j & Nebula Graph  是 图数据库（单独的软件，中间价） -》 脱离python
# neo4j 客户端

# 连接 Neo4j 数据库
graph = Graph('bolt://localhost:7687') # 本地的neo4j 数据库

# networkx 是 python的库

def clear_database():
    """清空数据库"""
    graph.delete_all()


def basic_operations():
    """基础 CRUD 操作"""
    # 创建节点
    alice = Node("Person", name="Alice", age=30, city="New York")
    bob = Node("Person", name="Bob", age=25, city="San Francisco")
    charlie = Node("Person", name="Charlie", age=35, city="Chicago")

    # 创建关系
    alice_knows_bob = Relationship(alice, "KNOWS", bob, since=2015)
    bob_knows_charlie = Relationship(bob, "KNOWS", charlie, since=2020)
    alice_works_with = Relationship(alice, "WORKS_WITH", charlie, project="AI Research")

    # 批量创建
    tx = graph.begin()
    tx.create(alice)
    tx.create(bob)
    tx.create(charlie)
    tx.create(alice_knows_bob)
    tx.create(bob_knows_charlie)
    tx.create(alice_works_with)
    graph.commit(tx)

    print("基础数据创建完成")


def query_examples():
    """查询示例"""
    # 使用 NodeMatcher
    matcher = NodeMatcher(graph)

    # 查找所有 Person 节点
    all_people = list(matcher.match("Person"))
    print(f"所有人员: {[person['name'] for person in all_people]}")

    # 条件查询
    young_people = list(matcher.match("Person").where(age__lt=30))
    print(f"年轻人: {[person['name'] for person in young_people]}")

    # 使用 Cypher 查询
    query = """
    MATCH (p:Person)-[r:KNOWS]->(friend:Person)
    RETURN p.name as person, friend.name as friend, r.since as since
    """
    result = graph.run(query)
    for record in result:
        print(f"{record['person']} 认识 {record['friend']} 从 {record['since']} 年开始")


clear_database()
basic_operations()
query_examples()