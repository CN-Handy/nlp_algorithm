import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# ... (Data loading and preprocessing remains the same) ...
dataset = pd.read_csv("../Week01/dataset.csv", sep="\t", header=None)

"""你是一个专业文本分析专家，请帮我对如下的文本进行分类：
还有双鸭山到淮阴的汽车票吗13号的
"""

"""你是一个专业文本分析专家，请帮我对如下的文本进行分类：
还有双鸭山到淮阴的汽车票吗13号的

可以参考的样本如下（假如已有的训练集）：
查询北京飞桂林的飞机是否已经起飞了	Travel-Query
从这里怎么回家	Travel-Query
随便播放一首专辑阁楼里的佛里的歌	Music-Play
给看一下墓王之王嘛	FilmTele-Play
我想看挑战两把s686打突变团竞的游戏视频	Video-Play
我想看和平精英上战神必备技巧的游戏视频	Video-Play

你只能从如下的类别选择：['FilmTele-Play', 'Video-Play', 'Music-Play', 'Radio-Listen',
       'Alarm-Update', 'Weather-Query', 'Travel-Query',
       'HomeAppliance-Control', 'Calendar-Query', 'TVProgram-Play',
       'Audio-Play', 'Other']
       
只需要输出结果，不需要额外的解释。
"""


from openai import OpenAI


# 云端大模型
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    # https://bailian.console.aliyun.com/?tab=model#/api-key
    api_key="sk-6b8dbf9ffdbf42188dbeb5df6b59fddd",

    # 大模型厂商的地址
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "user", "content": "你是谁？"}
    ]
)
print(completion.model_dump_json())