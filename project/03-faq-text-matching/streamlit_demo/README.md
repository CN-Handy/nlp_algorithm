# FAQ System Streamlit Demo

基于 Streamlit 的 Web 演示界面，用于测试和展示 FAQ 智能问答系统。

## 功能

- 📁 **类目管理** - 查看、创建、删除类目
- 📝 **FAQ管理** - 查看、创建、删除FAQ，添加答案
- 💬 **智能问答** - 基于语义理解的智能问答
- 🔍 **搜索** - 关键词搜索和目录导航

## 安装和运行

### 1. 安装依赖

```bash
cd streamlit_demo
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
# 在项目根目录
cd ..
uvicorn app.main:app --reload --port 8000
```

### 3. 启动 Streamlit

```bash
streamlit run Home.py
```

或使用指定端口：

```bash
streamlit run Home.py --server.port 8501
```

## 页面说明

| 文件 | 功能------|
| `Home.py` | |
|------| 主页面 |
| `pages/1_category.py` | 类目管理 |
| `pages/2_faq.py` | FAQ管理 |
| `pages/3_qa.py` | 智能问答 |
| `pages/4_search.py` | 搜索 |

## 配置

在 `config.py` 中修改 API 地址：

```python
API_BASE_URL = "http://localhost:8000"
```

## 截图预览

### 智能问答页面
- 输入问题
- 选择渠道 (默认/微信/App/网页)
- 返回匹配结果和答案

### 类目管理页面
- 查看类目列表和树形结构
- 创建/删除类目

### FAQ管理页面
- 查看FAQ列表
- 创建FAQ和答案
- 批量更新状态
