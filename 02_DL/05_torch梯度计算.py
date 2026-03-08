import torch

x = torch.ones(5, requires_grad=True)
y = x + 2 # element wise add
z = y * y * 3
out = z.mean()

print("自动求导:")
print(f"x: {x}")
print(f"y: {y}")
print(f"z: {z}")
print(f"out: {out}")

# 反向传播，计算梯度
out.backward()

# 打印梯度
print(f"x 的梯度: {x.grad}")
