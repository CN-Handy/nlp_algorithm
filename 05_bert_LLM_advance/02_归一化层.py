import torch
import torch.nn as nn

input_tensor = torch.randn(2, 3, 4, 4)
print(f"Input Tensor shape: {input_tensor.shape}\n")
print("-" * 40)


try:
    # 视觉任务中使用
    batchnorm_layer = nn.BatchNorm2d(num_features=3)
    batchnorm_output = batchnorm_layer(input_tensor)
    print(batchnorm_output)
except Exception as e:
    print(f"Error with BatchNorm2d: {e}")
print("-" * 40)

try:
    # Normalize the last three dimensions (channels, height, width)
    # NLP 常见的模型
    layernorm_layer = nn.LayerNorm(normalized_shape=[3, 4, 4])
    layernorm_output = layernorm_layer(input_tensor)
    print(layernorm_output)
except Exception as e:
    print(f"Error with LayerNorm: {e}")
print("-" * 40)


try:
    groupnorm_layer = nn.GroupNorm(num_groups=3, num_channels=3)
    groupnorm_output = groupnorm_layer(input_tensor)
    print(groupnorm_output)
except Exception as e:
    print(f"Error with GroupNorm: {e}")
print("-" * 40)