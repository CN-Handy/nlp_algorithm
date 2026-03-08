# pip install plotly pandas networkx
import openai
import json
import networkx as nx
import plotly.graph_objects as go
import re
from typing import List, Dict

# 初始化OpenAI客户端（使用阿里云百炼平台）
client = openai.OpenAI(
    # 填写你的 https://bailian.console.aliyun.com/?tab=model#/api-key
    api_key="sk-12ca7074269f49e1afaf221d496f727f",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def extract_relationships(content: str) -> Dict:
    """
    使用大模型从文本中抽取人物和关系
    """
    system_prompt = """你是一个关系抽取专家。请从给定的文本中提取所有人物以及他们之间的关系。
    请以JSON格式返回结果，包含两个字段：
    1. "entities": 人物列表，每个元素是一个人名
    2. "relationships": 关系列表，每个元素是一个字典，包含"source"（源人物）、"target"（目标人物）和"relation"（关系描述）

    示例输出格式：
    {
      "entities": ["张三", "李四", "王五"],
      "relationships": [
        {"source": "张三", "target": "李四", "relation": "父子"},
        {"source": "李四", "target": "王五", "relation": "同事"}
      ]
    }

    请确保只返回JSON格式的数据，不要有其他任何解释或文本。"""

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请从以下文本中提取人物和关系：\n\n{content}"},
            ],
        )

        response_text = completion.choices[0].message.content
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            print("未能从模型响应中提取JSON数据")
            return {"entities": [], "relationships": []}

    except Exception as e:
        print(f"调用模型时出错: {e}")
        return {"entities": [], "relationships": []}


def create_relationship_graph(entities: List[str], relationships: List[Dict]) -> nx.Graph:
    """
    根据抽取的实体和关系创建NetworkX图
    """
    G = nx.Graph()
    for entity in entities:
        G.add_node(entity)
    for rel in relationships:
        source = rel.get("source", "")
        target = rel.get("target", "")
        relation = rel.get("relation", "")
        if source and target and source in entities and target in entities:
            G.add_edge(source, target, relation=relation)
    return G


def draw_graph(G: nx.Graph, filename: str = "relationship_graph.html"):
    """
    绘制关系图并保存为HTML文件
    """
    # 使用spring布局获取节点位置
    pos = nx.spring_layout(G, k=1, iterations=50)

    # 创建边的轨迹
    edge_x = []
    edge_y = []
    edge_text = []  # 用于存储边的标签
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.append(edge[2]['relation'])

    # 创建边的 Plotly 散点图
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    # 创建节点轨迹
    node_x = []
    node_y = []
    node_text = []  # 用于存储节点的标签
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    # 创建节点的 Plotly 散点图
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            color=[],
            line_width=2))

    # 设置节点颜色
    node_adjacencies = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
    node_trace.marker.color = node_adjacencies

    # 创建边标签轨迹
    edge_label_x = []
    edge_label_y = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_label_x.append((x0 + x1) / 2)
        edge_label_y.append((y0 + y1) / 2)

    edge_label_trace = go.Scatter(
        x=edge_label_x, y=edge_label_y,
        text=edge_text,
        mode='text',
        hoverinfo='none'
    )

    # 创建布局和图表
    fig = go.Figure(data=[edge_trace, node_trace, edge_label_trace])

    # 保存图表为HTML文件
    fig.write_html(filename)
    print(f"关系图已成功保存为 '{filename}'")

    # 也可以选择展示图表
    fig.show()


def main():
    content = """谢广坤带着收养来的谢腾飞到村里卫生所看病，此时他的儿媳妇王小蒙已经去医院两天了，始终没传回来任何消息，焦急的他在村里大夫香秀给谢腾飞打了点滴过后，问香秀这方面的问题，香秀表示自己也不懂。实在等不及的他，给在医院产房外等待的儿子谢永强打电话，毫无结果。
    谢大脚超市里，谢大脚、刘能、王云三人在讨论王小蒙生孩子的事情，谢广坤这时来到超市给谢腾飞买罐头，听了刘能的话十分不满，让他先管好自家的事儿，之后便不多说就走了。刘能三人还在讨论着，看到谢广坤急匆匆的走出了村子，刘能趁机胡乱猜测，指责谢广坤抛弃腾飞。王云把话题扯开，问起刘英生孩子的事情，刘能因此说生孩子都是命这样的话，惹得谢大脚和王云两个没生育过的人都很不高兴。
    谢腾飞打完吊瓶后哭闹着找爷爷，无计可施的香秀只好带他去找他姥爷王老七。经过大脚超市，被谢大脚等三人给拦了下来。刘能追问腾飞是不是谢广坤把他丢下了，被谢大脚说了一顿。香秀把事情的原委说了一遍，刘能此时又说了些指责谢广坤的话，还煽动谢大脚等人一起去老徐那儿反应情况，谢大脚以超市离不开人为由，让他自己去。
    刘能气喘吁吁的来找正在自家院里修车的村书记老徐，添油加醋的说谢广坤把腾飞给扔了，为了让老徐重视这件事儿，还说这事关村里的荣誉，要老徐给谢广坤打电话把他叫回来。老徐给谢广坤打电话，谢广坤一心只想着去医院，交代完把腾飞送到亲家老七那儿以后就挂了电话。刘能知道后，又讨伐起谢广坤来。
    村主任赵玉田和母亲正在苗圃干活，这时他接到老丈人刘能打来的电话，要他开车把谢广坤追回来，赵玉田不解其意，刘能让老徐为作证，老徐拒绝，认为事情不像他说的那么严重。赵玉田把两人的对话听得一清二楚，要刘能有空到苗圃帮自己施肥，接着就挂了电话。他对刘能的态度让母亲说了一顿。
    王小蒙生了龙凤胎，刘永强给父亲谢广坤打了电话，在车上的谢广坤高兴得不得了，向全车的人宣布了这个好消息，还说要请车上所有人都去吃糖。为了能让村里的人尽早知道这个好消息，他中途下车，努力向着村里的方向飞奔。
    王老七到大脚超市去接谢腾飞，刘能见了煽风点火，说谢广坤对腾飞不好，还对腾飞说一些具有指引性的话，腾飞向众人表示，他的确被谢广坤打过，这消息震惊了所有人。刘能非要王老七打电话训斥谢广坤的行为，老七劝他别惹事，他一意孤行，要给谢广坤打电话，反被谢广坤挂断了。
    刘能还在谢大脚的超市门前挑事儿，表示一定要找到谢广坤教训他，这时被老徐指责对村里事物不上心的赵玉田回到村里，看到聚集在大脚超市门前的人还有哭泣的老丈人刘能，上前询问。此刻，跑得满头大汗的谢广坤来到众人面前，累得说不出话的他根本停不下来，瘫倒在了地上，在缓过气后，他结结巴巴，在吓到所有人之后，终于说出了王小蒙生了龙凤胎的事儿。没想到刘能听了这话，直接翻了白眼，不省人事，在众人的救护下，他苏醒过来，提议要隆重办个庆典。
    """

    print("正在从文本中抽取人物关系...")
    result = extract_relationships(content)
    print("抽取结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    G = create_relationship_graph(result["entities"], result["relationships"])

    print("\n正在绘制关系图...")
    draw_graph(G)

    print(f"人物数量: {G.number_of_nodes()}")
    print(f"关系数量: {G.number_of_edges()}")
    print("人物列表:", list(G.nodes()))
    print("关系列表:", [(u, v, d['relation']) for u, v, d in G.edges(data=True)])


if __name__ == "__main__":
    main()