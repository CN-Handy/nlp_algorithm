import numpy as np

# 从 Python 列表创建一维数组
arr1d = np.array([1, 2, 3, 4, 5])
print(f"一维数组: {arr1d}")
print(f"数组的维度: {arr1d.shape}")

# 从 Python 嵌套列表创建二维数组（矩阵）
arr2d = np.array([[1, 2, 3],
                  [4, 5, 6]])
print("\n二维数组:")
print(arr2d)
print(f"数组的维度: {arr2d.shape}")

# 使用内置函数创建数组
zeros_arr = np.zeros((2, 3)) # 创建一个2x3的零矩阵
print("\n零矩阵:")
print(zeros_arr)

ones_arr = np.ones((3, 2)) # 创建一个3x2的一矩阵
print("\n一矩阵:")
print(ones_arr)

range_arr = np.arange(10) # 创建一个0到9的数组
print(f"\n0到9的数组: {range_arr}")

# 默认数据类型为 int64
int_arr = np.array([1, 2, 3])
print(f"整数数组的数据类型: {int_arr.dtype}")

# 指定数据类型为 float32
float_arr = np.array([1, 2, 3], dtype=np.float32)
print(f"浮点数数组的数据类型: {float_arr.dtype}")
print(f"浮点数数组: {float_arr}")

# 也可以指定为其他类型，例如布尔型
bool_arr = np.array([0, 1, 0], dtype=bool)
print(f"布尔数组: {bool_arr}")

# 创建两个矩阵
A = np.array([[1, 2],
              [3, 4]])
B = np.array([[5, 6],
              [7, 8]])
print("\n矩阵 A:")
print(A)
print("\n矩阵 B:")
print(B)

# 元素级相加
print("\n矩阵 A + B (元素级相加):")
print(A + B)

# 元素级相乘
print("\n矩阵 A * B (元素级相乘):")
print(A * B)

# 矩阵乘法（点积），使用 @ 运算符或 np.dot()
print("\n矩阵乘法 A @ B:")
print(A @ B)

# 矩阵转置
print("\n矩阵 A 的转置:")
print(A.T)

# 假设我们有一些训练数据
# x 代表输入特征（例如，学习时长）
# y 代表输出标签（例如，考试分数）
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 5, 4, 5])

# 计算 x 和 y 的平均值
x_mean = np.mean(x)
y_mean = np.mean(y)

# 计算线性回归的斜率（slope）和截距（intercept）
# 斜率（b1）的公式：b1 = Σ((xi - x_mean) * (yi - y_mean)) / Σ((xi - x_mean)^2)
# 截距（b0）的公式：b0 = y_mean - b1 * x_mean

numerator = np.sum((x - x_mean) * (y - y_mean))
denominator = np.sum((x - x_mean) ** 2)

b1 = numerator / denominator
b0 = y_mean - b1 * x_mean

print("\n--- 线性回归结果 ---")
print(f"数据的 x 平均值: {x_mean}")
print(f"数据的 y 平均值: {y_mean}")
print(f"计算出的斜率 (b1): {b1:.2f}")
print(f"计算出的截距 (b0): {b0:.2f}")

# 预测新数据
x_new = 6
y_pred = b1 * x_new + b0
print(f"\n如果学习时长为 {x_new} 小时，预测的考试分数为: {y_pred:.2f}")