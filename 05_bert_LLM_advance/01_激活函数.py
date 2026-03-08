import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('seaborn-v0_8-whitegrid')

# 创建一个 nn.Softmax 实例
# dim=0 表示对第一维（行）进行 Softmax
# dim=1 表示对第二维（列）进行 Softmax
# 在这里，我们的输入张量是二维的，所以 dim=1
softmax_layer = nn.Softmax(dim=1)

# 创建一个示例输入张量
# 形状为 (2, 3)，表示 2 个样本，每个样本有 3 个特征/类别
input_tensor = torch.tensor([[1.0, 2.0, 3.0],
                             [4.0, 5.0, 6.0]])

# 应用 Softmax
output_softmax = softmax_layer(input_tensor)

print("原始输入张量:")
print(input_tensor)
print("\n应用 Softmax 后的张量:")
print(output_softmax)
print("\nSoftmax 输出的每行之和:")
print(torch.sum(output_softmax, dim=1))

def plot_activation(activation_func, title, ax):
    """
    可视化给定的激活函数。
    :param activation_func: PyTorch nn.Module 激活函数实例
    :param title: 图表的标题
    :param ax: Matplotlib 的 Axes 对象
    """
    # 创建一个在 -5 到 5 之间，包含 1000 个点的输入张量
    x = torch.linspace(-5, 5, 1000)

    # 对于 GLU，需要一个特殊的输入，因为它是 Gated Linear Unit
    if isinstance(activation_func, nn.GLU):
        # GLU 需要一个偶数维度的输入，并将其分成两半
        input_dim = 2
        x_glu = torch.linspace(-5, 5, 1000).view(-1, 1).repeat(1, input_dim)
        y = activation_func(x_glu).data.numpy()
        x = x_glu[:, 0].numpy()
        ax.plot(x, y.reshape(-1), label='Output (first half)')
        ax.plot(x, y.reshape(-1), linestyle='--', label='Output (second half)')
        ax.legend()
    else:
        # 对于其他激活函数，直接应用
        y = activation_func(x).data.numpy()
        ax.plot(x.numpy(), y)

    ax.set_title(title)
    ax.set_xlabel('Input (x)')
    ax.set_ylabel('Output (y)')
    ax.grid(True)

# 创建一个字典，包含所有要演示的激活函数
activations = {
    'ReLU': nn.ReLU(),
    'ReLU6': nn.ReLU6(),
    'LeakyReLU': nn.LeakyReLU(negative_slope=0.1),
    'PReLU': nn.PReLU(),
    'RReLU': nn.RReLU(),
    'ELU': nn.ELU(),
    'SELU': nn.SELU(),
    'CELU': nn.CELU(),
    'GELU': nn.GELU(),
    'Sigmoid': nn.Sigmoid(),
    'LogSigmoid': nn.LogSigmoid(),
    'Tanh': nn.Tanh(),
    'Softplus': nn.Softplus(),
    'Softsign': nn.Softsign(),
    'SiLU (Swish)': nn.SiLU(),
    'Mish': nn.Mish(),
    'Hardtanh': nn.Hardtanh(),
    'Hardswish': nn.Hardswish(),
    'Hardsigmoid': nn.Hardsigmoid(),
    'Hardshrink': nn.Hardshrink(),
    'Softshrink': nn.Softshrink(),
    'Tanhshrink': nn.Tanhshrink(),
    'Threshold': nn.Threshold(threshold=0.5, value=0.1),
    'GLU': nn.GLU()
}

# 准备绘图
num_activations = len(activations)
cols = 6
rows = (num_activations + cols - 1) // cols  # 计算行数

fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows))
axes = axes.flatten()

# 遍历字典，对每个激活函数进行演示和绘图
for i, (name, activation) in enumerate(activations.items()):
    ax = axes[i]
    plot_activation(activation, name, ax)

# 隐藏多余的子图
for i in range(num_activations, len(axes)):
    fig.delaxes(axes[i])

plt.tight_layout()
plt.show()