# https://github.com/openai/openai-agents-python
# pip install -qU openai-agents
import os
os.environ["OPENAI_API_KEY"] = "sk-f0ab3fca58044adcb75b5a60974549b3"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# openai-agents 是 openai 推出的一个agent开发框架，agent 本质就是大模型调用
# langgraph 框架，基于 langchain 封装的 agent 框架，agent 程序 通过图的方式进行搭建，节点、边；

from agents import Agent, Runner # agent 应用开发 智能体搭建
from agents import Agent, OpenAIConversationsSession, Runner
session = OpenAIConversationsSession()

from agents import set_default_openai_api, set_tracing_disabled
set_default_openai_api("chat_completions")
set_tracing_disabled(True)

# openai-agnet框架中，agent 本质就是大模型调用
agent1 = Agent(model="qwen-max", name="Assistant", instructions="你的名字是小王。")
agent2 = Agent(model="qwen-max", name="Assistant", instructions="你的名字是小李。")

result = Runner.run_sync(agent1, "你好", session=session,)
print(result.final_output)

result = Runner.run_sync(agent2, "上一句我问的是什么？直接回答。", session=session,)
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.

# https://github.com/openai/openai-agents-python/tree/main/examples