import os
from dashscope import MultiModalConversation

# 将xxx/eagle.png替换为你本地图像的绝对路径
local_path = "./cardboard1.jpg"
image_path = f"file://{local_path}"
messages = [{"role": "system",
                "content": [{"text": "You are a helpful assistant."}]},
                {'role':'user',
                'content': [{'image': image_path},
                            {'text': '识别图片中垃圾的类型，待选类型包括cardboard, glass, metal, paper, plastic and trash'}]}]
response = MultiModalConversation.call(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key="sk-7d288f775de84c33a2b065d2e69d5481",
    model='qwen-vl-max-latest',  # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/models
    messages=messages)
print(response["output"]["choices"][0]["message"].content[0]["text"])