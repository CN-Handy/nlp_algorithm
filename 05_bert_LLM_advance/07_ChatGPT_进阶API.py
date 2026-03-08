import openai
import json

client = openai.OpenAI(
    api_key="sk-pL9wStGbuCTF5uV9971eE079089f4c3e8fD0A52eAdCe08E0",
    base_url="https://openkey.cloud/v1"
)


response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content":
"""
请帮我进行文本分类，判断下面的文本是正向情感还是负面情感。请直接输出类别，不要有其他输出，可选类别：正/负

我今天很开心。
"""}],
    stream=False, # 非流式 输出，等输出完成了一起返回
    logprobs = True, # 带上每个token的log（概率），chatgpt 支持的
    top_logprobs = 5 # 每个top 5 token
)
print(response) # token 的概率 -》 大模型很自信？幻觉存在？ 幻觉检测的方法

# 大模型的生成结果是token 的概率输出，输出输出并不一定有逻辑；



# 大模型进行 进行对话过程中，无论你是否传入了funciton call 函数的定义，自回归逐步输出；
# 经验1: 100个待选函数，非常消耗token，速度很慢， 建议10个或更少的待选函数；
# 经验2: 文本 -》 一次函数调用的过程； 不能选择调用两个函数，或 嵌套函数；
# 经验3: 函数的定义json 可以人工写，但推荐自动生成

# function call / tools -》 自然语言 转换为 调用什么函数？ 调用函数的参数 -> agent
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "今天是25年9月7日，帮我查询下北京在昨天的天气。"},
    ],

    # tools 后期的概念，本质也是 function call

    # functions 列表， 存储待选函数的定义
    functions=[
        {
            "name": "get_weather",
            "description": "查询城市在某一天的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市"
                    },
                    "date_str": {
                        "type": "string",
                        "description": "日期"
                    },
                },
                "required": ["city", "date_str"]
            }
        }
    ]
)

print(response.model_dump_json(indent=4))

def get_weather(city, date_str):
    # 模拟的查询天气的函数
    print(f"### 查询天气返回结果：{city}  {date_str} 是晴天")


if response.choices[0].message.function_call:
    function_name = response.choices[0].message.function_call.name
    function_args_str = response.choices[0].message.function_call.arguments

    # 将 JSON 字符串解析为 Python 字典
    function_args = json.loads(function_args_str)

    print(f"\n模型请求调用函数: {function_name}")
    print(f"参数: {function_args}\n")

    # --- 推荐的、更安全的方法 ---
    # 使用函数映射来调用本地函数，这比 eval 更安全
    function_map = {
        "get_weather": get_weather
    }

    if function_name in function_map:
        local_function = function_map[function_name]
        result = local_function(**function_args)
        print(result)
