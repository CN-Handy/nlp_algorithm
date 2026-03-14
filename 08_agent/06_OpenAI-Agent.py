# https://github.com/openai/openai-agents-python
# pip install -qU openai-agents
import os
os.environ["OPENAI_API_KEY"] = "sk-4806ae58c8de41848fd1153108c3d86c"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

from agents import Agent, Runner
from agents import set_default_openai_api, set_tracing_disabled
set_default_openai_api("chat_completions")
set_tracing_disabled(True)

agent = Agent(model="qwen-max", name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.

# https://github.com/openai/openai-agents-python/tree/main/examples