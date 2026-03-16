# FAQ System HTTP API Tests

## 安装依赖

```bash
pip install -r tests/requirements.txt
```

## 运行测试

### 运行所有测试
```bash
pytest tests/ -v
```

### 运行特定模块测试
```bash
# 类目管理测试
pytest tests/test_categories.py -v

# FAQ 核心测试
pytest tests/test_faqs.py -v

# 对外服务测试
pytest tests/test_service.py -v
```

### 运行特定测试用例
```bash
pytest tests/test_service.py::TestSmartQA::test_ask_question_wechat_channel -v
```

### 显示详细输出
```bash
pytest tests/ -v -s
```

## 测试文件说明

| 文件 | 说明 |
| --- | --- |
| `conftest.py` | pytest 配置和 fixtures |
| `test_categories.py` | 类目管理 API 测试 |
| `test_faqs.py` | FAQ 核心 API 测试 |
| `test_service.py` | 对外服务模块 (Bot Service) API 测试 |

## 配置

在 `conftest.py` 中修改 `BASE_URL` 以匹配你的服务器地址：

```python
BASE_URL = "http://localhost:8000"  # 修改为实际地址
```

## 测试覆盖

### 类目管理
- [x] 创建一级/二级类目
- [x] 获取类目树
- [x] 修改类目
- [x] 删除类目（软删除）
- [x] 删除有关联FAQ的类目

### FAQ 核心
- [x] 创建/修改/删除 FAQ
- [x] 添加多视角答案
- [x] 切换 FAQ 状态
- [x] 批量导入/导出
- [x] 参数验证

### 对外服务
- [x] 智能问答（多渠道）
- [x] 自助导航
- [x] FAQ 详情获取
- [x] 关联推荐
- [x] 完整流程集成测试
