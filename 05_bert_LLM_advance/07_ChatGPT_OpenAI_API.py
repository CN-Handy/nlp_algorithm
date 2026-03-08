# 基于 openai 客户端的使用
import openai # pip install openai

client = openai.OpenAI(
    # 认证 ， 计费
    api_key="sk-pL9wStGbuCTF5uV9971eE079089f4c3e8fD0A52eAdCe08E0",

    # 访问的大模型厂商的基础信息
    base_url="https://openkey.cloud/v1"
)

# {base_url}/chat/completions
for resp in client.chat.completions.create(
    model="gpt-3.5-turbo", # 厂商支持的模型代号
    messages=[
        {"role": "user", "content": "帮我讲一个笑话，要200字"}, # 大模型输出长度由设置的maxlen 和 【eos】决定的，大模型本身不支持生成了多长；
    ],
    stream=True # 模型生成一个token ，返回给我
):
    if resp.choices and resp.choices[0].delta.content:
        print(resp.choices[0].delta.content, end="\n", flush=True)

"""
！” token
老 token
"""