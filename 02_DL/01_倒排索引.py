import pandas as pd
import jieba

dataset = pd.read_csv("./dataset.csv", sep="\t", header=None)
print(dataset.head(5))

inverted_index = {} # 倒排索引， 每个单词 对应的 文档
for index, row in dataset.iterrows():
    text = row[0]
    words = jieba.cut(text)  # Tokenize the text
    for word in words:
        if word not in inverted_index:
            inverted_index[word] = set()
        inverted_index[word].add(index)

def search(query):
    query_words = jieba.cut(query)
    results = None
    for word in query_words:
        if word in inverted_index:
            if results is None:
                results = inverted_index[word].copy()
            else:
                results &= inverted_index[word]
        else:
            return []

    if results is None:
        return []

    return list(results)

query1 = "汽车票"
result_indices1 = search(query1)
print(f"搜索 '{query1}' 的结果:")
print(dataset.iloc[result_indices1].head(3))

print("\n" + "=" * 50 + "\n")

query2 = "双鸭山到淮阴"
result_indices2 = search(query2)
print(f"搜索 '{query2}' 的结果:")
print(dataset.iloc[result_indices2].head(3))