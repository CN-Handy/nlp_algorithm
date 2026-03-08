# sklearn 代码
# 逻辑回归：分类模型
# 加载给定的数据 sklearn

from sklearn import linear_model # 线性模型模块
from sklearn import tree # 决策树模块
from sklearn import datasets # 加载数据集
from sklearn.model_selection import train_test_split # 数据集划分
from sklearn import neighbors

data = datasets.load_iris() # 植物分类的数据集
X, y = data.data, data.target # 0 1 2, 植物的三种类型

# 100个样本 -》 100个标签
# X 100 * 4 矩阵
# 每行是一个样本
# 列是一个字段/特征

model = linear_model.LogisticRegression(max_iter=1000)
model.fit(X, y) # fit 就是训练模型
print(model)

# random_state random_seed 随机种子，控制随机数的生成
# 固定了，则生成的随机数就固定了

train_x, test_x, train_y, test_y = train_test_split(X, y, random_state=520) # 数据切分 25% 样本划分为测试集
# 训练集：调整模型的参数 （练习题、知道答案）
# 测试集：验证模型的精度 （摸底考试，不知道答案）
print(train_y)
print("真实标签", test_y)

model = linear_model.LogisticRegression(max_iter=1000) # 模型初始化， 人工设置的参数叫做超参数， 模型参数可以从训练集学习到的
model.fit(train_x, train_y)
prediction = model.predict(test_x)
print("预测结果", prediction)
print("逻辑回归的预测结果", (test_y == prediction).sum(), len(test_x)) # element wise equal

model = tree.DecisionTreeClassifier() # 模型初始化
model.fit(train_x, train_y)
prediction = model.predict(test_x)
print("预测结果", prediction)
print("决策树的预测结果", (test_y == prediction).sum(), len(test_x))


model = neighbors.KNeighborsClassifier(n_neighbors=1) # 模型初始化
model.fit(train_x, train_y)
prediction = model.predict(test_x)
print("预测结果", prediction)
print("1-KNN的预测结果", (test_y == prediction).sum(), len(test_x))


model = neighbors.KNeighborsClassifier(n_neighbors=3) # 模型初始化
model.fit(train_x, train_y)
prediction = model.predict(test_x)
print("预测结果", prediction)
print("3-KNN的预测结果", (test_y == prediction).sum(), len(test_x))

# 搜索、遍历
# or
# 人工设置（了解模型）
for k in [1,3,5,7,9]:
    model = neighbors.KNeighborsClassifier(n_neighbors=k) # 模型初始化
    model.fit(train_x, train_y) # lazy learning，没有做任何事情
    prediction = model.predict(test_x) # 遇到新的样本
    print("预测结果", prediction)
    print(f"{k}-KNN的预测结果", (test_y == prediction).sum(), len(test_x))

