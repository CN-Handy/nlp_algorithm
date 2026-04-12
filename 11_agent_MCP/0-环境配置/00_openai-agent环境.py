# https://github.com/openai/openai-agents-python
# pip install -qU openai-agents        核心的sdk
# pip install "openai-agents[viz]"     可以不安装，agent的可视化

import os

# https://bailian.console.aliyun.com/?tab=model#/api-key
os.environ["OPENAI_API_KEY"] = "sk-f9bac974cf79404691f92e06f567ea27"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

from agents import Agent, Runner
from agents import set_default_openai_api, set_tracing_disabled
set_default_openai_api("chat_completions")
set_tracing_disabled(True)


# agent的定义
agent = Agent(
    model="qwen-max", # 模型代号
    name="Assistant", # 给agent的取得名字（推荐英文，写的有意义）
    instructions="You are a helpful assistant" # 对话中的 开头 system message
)

# 接受用户输入，构建对话 调用大模型 得到输出
result = Runner.run_sync(agent, "帮我写一个对联。") # 同步运行，输入 user messgae
result = Runner.run_sync(agent, "帮我写一个对联。") # 同步运行，输入 user messgae
result = Runner.run_sync(agent, "帮我写一个对联。") # 同步运行，输入 user messgae

print(result.final_output)

"""
{
    "role": "system",
    "content": "You are a helpful assistant"
}
{
    "role": "user",
    "content": "帮我写一个对联。"
}
"""


# python 00_openai-agent环境.py