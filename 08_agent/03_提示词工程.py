import openai
import json

client = openai.OpenAI(
    api_key="sk-4806ae58c8de41848fd1153108c3d86c", # https://bailian.console.aliyun.com/?tab=model#/api-key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "user", "content": """对下面的文本划分为 Travel-Query / Video-Play / FilmTele-Play 其中的一种。
输入：还有双鸭山到淮阴的汽车票吗13号的
类别："""},
    ],
)
print("\nZero-Shot Prompting")
print(completion.choices[0].message.content)



completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "user", "content": """对下面的文本划分为 Travel-Query / Video-Play / FilmTele-Play 其中的一种。
输入：我想看挑战两把s686打突变团竞的游戏视频
类别：Video-Play

输入：查询北京飞桂林的飞机是否已经起飞了
类别：Travel-Query
        
输入：还有双鸭山到淮阴的汽车票吗13号的
类别："""},
    ],
)
print("\nFew-Shot Prompting")
print(completion.choices[0].message.content)


# 其他方法
# https://www.promptingguide.ai/techniques