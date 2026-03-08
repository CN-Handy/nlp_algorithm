import os

# pip install openai
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    # https://bailian.console.aliyun.com/?tab=model#/api-key
    api_key="sk-7d288f775de84c33a2b065d2e69d5481", # 账号绑定的

    # 大模型厂商的地址
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus", # 模型的代号

    messages=[
        {"role": "system", "content": "You are a helpful assistant."}, # 给大模型的命令，角色的定义
        {"role": "user", "content": "你是谁？"},  # 用户的提问
        {"role": "user", "content": "你是谁？"},  # 用户的提问
    ]
)
print(completion.choices[0].message.content)