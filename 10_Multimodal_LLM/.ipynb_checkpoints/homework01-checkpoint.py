from transformers import ChineseCLIPProcessor, ChineseCLIPModel
from modelscope import snapshot_download
from PIL import Image
from sklearn.preprocessing import normalize
import torch
import numpy as np

model_name = "AI-ModelScope/chinese-clip-vit-base-patch16"
model_path = snapshot_download(model_name)

model = ChineseCLIPModel.from_pretrained(model_path)
processor = ChineseCLIPProcessor.from_pretrained(model_path)

img = Image.open("./images/dog.jpg")
img_input = processor(images=img, return_tensors="pt")
with torch.no_grad():
    img_feature = model.get_image_features(**img_input)
    img_feature = img_feature.data.numpy()

img_feature = normalize(img_feature)

img_classification = ['兔子', '小狗', '小猫', '牛', '羊', '鸡', '猪', '小马', '青蛙']
classification_inputs = processor(text=img_classification, return_tensors="pt", padding=True)
with torch.no_grad():
    classification_feature = model.get_text_features(**classification_inputs)
    classification_feature = classification_feature.data.numpy()

classification_feature = normalize(classification_feature)

sim_result = np.dot(img_feature, classification_feature.T)
sim_index = np.argmax(sim_result)

print(f"使用CLIP进行图片分类的结果是：{img_classification[sim_index]}")
