# pip install -qU "langchain[openai]"
import os
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

os.environ["OPENAI_API_KEY"] = "sk-4806ae58c8de41848fd1153108c3d86c"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

model = init_chat_model("qwen-plus", model_provider="openai")

system_template = "Translate the following from English into {language}"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

prompt = prompt_template.invoke({"language": "中文", "text": "hi!"}) # invoke 调用大模型
print(prompt.to_messages())

response = model.invoke(prompt)
print(response.content)

"""
{"role": "system", content: "Translate the following from English into 中文"}
{"role": "user", conent: "hi"}
"""
