from sentence_transformers import SentenceTransformer
# 必备库，基于transformers，用途是做模型推理、sbert训练过程的用途
# sentence_transformers 作者 就是 sbert论文 的作者

# 上一节课 下载的 模型
# "../models/google-bert/bert-base-chinese/"
model = SentenceTransformer("../models/google-bert/bert-base-chinese/") # 没有暴露tokenizer、 model

sentences = [
    "我今天很开心", # 768 512
    "我今天很不开心",
    "我要去吃海底捞"
]

embeddings = model.encode(sentences) # 正向传播 -》 句子编码 （token的编码 -》 mean pooling）
print(embeddings.shape)

similarities = model.similarity(embeddings, embeddings)
print(similarities)

# modelscope download --model BAAI/bge-small-zh-v1.5  --local_dir BAAI/bge-small-zh-v1.5
# https://huggingface.co/spaces/mteb/leaderboard
model = SentenceTransformer("../models/BAAI/bge-small-zh-v1.5/") # sentence-bert 微调之后的
embeddings = model.encode(sentences)
print(embeddings.shape)

similarities = model.similarity(embeddings, embeddings)
print(similarities)

"""
文本库有 200 个样本
用户有2个提问
任务： 在文本库中找到与用户提问相似的样本

BERT NSP： 句子1 和 句子2  拼接为一个输入， 送到bert 提取特征，做分类
SBERT： 分别对 句子1 句子2 提取特征，计算相似度

如果没有任何提前操作：
- BERT NSP： 2 个提问 * 200待选文本 -》 400 BERT 正向传播
- SBERT： 2提问，200待选文本 -》 202 BERT 正向传播

提前对文本库提取特征：
- BERT NSP： 2 个提问 * 200待选文本 -》 400 BERT 正向传播
- SBERT： 2提问 -》 2 BERT 正向传播
"""
