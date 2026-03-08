import numpy as np
import requests

# 仔细读一遍 https://platform.openai.com/docs/overview
# 基本一致 https://bailian.console.aliyun.com/cn-beijing/?tab=api#/api/?type=model&url=3016807

# https://openkey.cloud/
# https://f2api.com/docs/openai/price

url = "https://openkey.cloud/v1/chat/completions" # gpt api 地址

# openkey.cloud vs 阿里云百练
# openkey.cloud 模型转发， 调用国外的模型
# 阿里云百练 模型厂商，自己部署了模型，没有国外的模型

headers = {
    'Content-Type': 'application/json',
    # <-- 把 fkxxxxx 替换成你自己的 Forward Key，注意前面的 Bearer 要保留，并且和 Key 中间有一个空格
    'Authorization': 'Bearer sk-pL9wStGbuCTF5uV9971eE079089f4c3e8fD0A52eAdCe08E0' # token 计费相关
}

data = {
  "model": "gpt-3.5-turbo",
  "messages": [
      {"role": "user", "content": "我很开心，哈哈哈"},
      {'role': "assistant", "content": "很高兴了解你感到开心！继续保持好心情！有什么需要帮忙的可以告诉我。"},
      {"role": "user", "content": "我就不告诉你。"}
  ]
}

# 历史提问都拼接一起，生成后序token
response = requests.post(url, headers=headers, json=data)
print("Status Code", response.status_code)
print("JSON Response ", response.json())



data = {
  "model": "gpt-3.5-turbo",
  "messages": [
      {"role": "user", "content": "你好！给我讲个笑话。"},
      {"role": "user", "content": "我就不告诉你。"}
  ]
}
response = requests.post(url, headers=headers, json=data)
print("Status Code", response.status_code)
print("JSON Response ", response.json())




url = "https://openkey.cloud/v1/embeddings"

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer sk-pL9wStGbuCTF5uV9971eE079089f4c3e8fD0A52eAdCe08E0' # <-- 把 fkxxxxx 替换成你自己的 Forward Key，注意前面的 Bearer 要保留，并且和 Key 中间有一个空格。
}

data = {
    "model": "text-embedding-ada-002", # 编码模型， gpt 训练得到的，不是一个bert模型 =》 实现功能 类似 sbert
    "input": "魔兽世界坐骑去哪买" # 待编码的文本
}
# HTTP的调用
response = requests.post(url, headers=headers, json=data)
arr1 = np.array(response.json()['data'][0]['embedding'])

data = {
    "model": "text-embedding-ada-002",
    "input": "奥比岛在哪有皇室舞会的邀请函？"
}
response = requests.post(url, headers=headers, json=data)
arr2 = np.array(response.json()['data'][0]['embedding'])

print(np.dot(arr1, arr2))
