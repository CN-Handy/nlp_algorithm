# pip install -qU "langchain[openai]"
import os
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage # 大模型调用时候，role

# qwen 地址代替 openai
os.environ["OPENAI_API_KEY"] = "sk-4806ae58c8de41848fd1153108c3d86c"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 调用方式1
# 初始化客户端
chatLLM = ChatOpenAI(
    api_key="sk-4806ae58c8de41848fd1153108c3d86c",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",
)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "你是谁？"}
]
response = chatLLM.invoke(messages)
print(response.json())

# 调用方式2
model = init_chat_model("qwen-plus", model_provider="openai")
messages = [
    HumanMessage(content="你是谁？"),
]

print(model.invoke(messages))