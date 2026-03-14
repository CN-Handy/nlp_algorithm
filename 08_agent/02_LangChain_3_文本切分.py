# pip install -qU "langchain[openai]"
# pip install -qU langchain-text-splitters tiktoken

# langchain[openai] 底层模块的库
# langchain-text-splitters rag文本切分的逻辑

# rag 中存在很多文本切分方法
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    MarkdownTextSplitter,
    HTMLSectionSplitter,
    SentenceTransformersTokenTextSplitter,
)

state_of_the_union = """
《乡村爱情》系列剧的主题曲和片尾曲主要由赵本山和本山传媒旗下的歌手及音乐人担任创作和演唱。其中主题曲《咱们屯里的人》广为知名，2015年，歌手罗凯楠模仿香港艺人刘德华的唱腔以类似粤语的发音翻唱了这首东北风情的歌曲，作为开心麻花团队沈腾、马丽主演的电影《夏洛特烦恼》的插曲，引起强烈反响。其后，贺岁片《澳门风云3》的片尾曲《恭喜发财2016》中，刘德华用粤语亲自演唱了这首歌部分段落。《王牌逗王牌》（又名：偷天特务）中，刘德华与沈腾再次合唱了这首歌。

赵本山回应观众质疑该剧是伪现实主义时说：“我敢说，农村生活在座的各位没有比我更了解的，我是你们的老师，就不要唠农村了，如果唠城里的事，我赶紧缴枪不杀。”而专家们[谁？]指责该剧放大人物身体缺陷以博得笑声，该片不能代表农村现状。赵本山回应说：“我从来都不是高雅的人，也最恨那些自命不凡、认为自己有文化，而实际在误人子弟的一批所谓教授。”赵本山提出教授们如果没有去过农村，没有体验过农村人的生活，就没有发言权。[12]
"""

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=50,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)
texts = text_splitter.create_documents([state_of_the_union])
print("RecursiveCharacterTextSplitter")
print(texts[0])
print(texts[1])


text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4",
    chunk_size=50,
    chunk_overlap=20
)
texts = text_splitter.create_documents([state_of_the_union])
print("RecursiveCharacterTextSplitter")
print(texts[0])
print(texts[1])

