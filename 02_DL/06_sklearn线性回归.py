import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# 1. 生成模拟数据 (与之前相同)
X_numpy = np.random.rand(100, 1) * 10
y_numpy = 2 * X_numpy + 1 + np.random.randn(100, 1)

plt.figure(figsize=(10, 6))
plt.plot(X_numpy, y_numpy, 'b.', alpha=0.6, label='原始数据', color='blue')
plt.show()

model = LinearRegression()
model.fit(X_numpy, y_numpy)

print(model.coef_, model.intercept_)