# 客服工作台与智能问答系统 (CS-Workstation & AI-FAQ System)

本项目是一款集成了 **多渠道接入、双环境 FAQ 管理、智能语义搜索**综合服务平台。系统采用 Python 异步生态构建，旨在平衡机器人自动化效率与人工服务的深度协作。

## 核心特性

* **双环境隔离机制**：“测试环境配置 $\rightarrow$ 模拟验证 $\rightarrow$ 发布中心一键同步 $\rightarrow$ 正式环境生效”流程管理。
* **多维 FAQ 体系**：
    * 支持**类目树管理**（一/二级类目）。
    * **多视角答案**：同一问题可针对微信、App、网页等不同渠道返回差异化答案。
    * **多类型支持**：纯文本、富文本（图文/附件/视频）、交互式卡片。
* **高性能架构**：基于 FastAPI 异步 IO，支持高并发长连接（WebSocket）。


## 技术栈

| 领域 | 技术选型 | 备注 |
| --- | --- | --- |
| **核心框架** | **FastAPI** | 基于 ASGI 的高性能异步 Web 框架 |
| **数据库** | **MySQL + SQLAlchemy 2.0** | 采用异步驱动（aiomysql）处理业务逻辑 |
| **缓存** | **Redis** | 缓存热点数据，避免重复查询数据库 |
| **搜索引擎** | **Elasticsearch 8.x** | 全文检索 + 向量搜索 (dense_vector)，支持语义相似匹配 |
| **Embedding** | **Sentence-Transformers** | 本地模型生成向量，用于语义搜索 |

## 数据库设计

1. 类目管理表 (categories)

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| **id** | Integer (PK) | 类目唯一标识 |
| **env** | Enum | **环境标识**：`TEST` (测试), `PROD` (正式) |
| **name** | String(64) | 类目名称 |
| **parent_id** | Integer | 父类目 ID (关联本表的 id) |
| **level** | Integer | 层级 (1-一级, 2-二级) |
| **original_id** | Integer | **溯源 ID**：正式环境记录指向其来源的测试环境 ID |
| **creator/modifier** | String(64) | 操作人审计 |
| **created/updated_at** | DateTime | 时间审计 |

2. FAQ 主表 (faqs)

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| **id** | Integer (PK) | FAQ 唯一标识 |
| **env** | Enum | **环境标识**：`TEST` (测试), `PROD` (正式) |
| **category_id** | Integer | 关联 `categories.id` (需对应相同 env) |
| **title** | String(255) | **标准问标题** |
| **status** | Enum | 生效状态：`ENABLE` (生效), `DISABLE` (失效) |
| **is_permanent** | Boolean | 是否永久生效 |
| **start/end_time** | DateTime | 生效时间区间 |
| **answer_type** | Enum | 类型：`TEXT` (纯文本), `RICH` (富文本), `CARD` (卡片) |
| **content** | Text | 答案具体内容 |
| **creator/modifier** | String(64) | 创建人和修改人 |
| **created/updated_at** | DateTime | 创建时间和更新时间 |

## 核心流程

1. 知识生产与管理模块

| 功能子模块 | 接口路径 (Endpoint) | 方法 | 描述 |
| --- | --- | --- | --- |
| **类目管理** | `/api/v1/admin/categories` | **POST** | **新建类目**：支持一、二级层级创建。 |
|  | `/api/v1/admin/categories/{id}` | **PUT** | **修改类目**：更新类目名称或排序。 |
|  | `/api/v1/admin/categories/{id}` | **DELETE** | **删除类目**：校验下属是否有FAQ，支持物理/软删除。 |
|  | `/api/v1/admin/categories/tree` | **GET** | **获取类目树**：按环境返回完整的层级结构。 |
| **FAQ 核心** | `/api/v1/admin/faqs` | **POST** | **新建FAQ**：录入标准问及相似问法。 |
|  | `/api/v1/admin/faqs/{id}` | **PUT** | **修改FAQ**：更新基础问法与关联问题设置。 |
|  | `/api/v1/admin/faqs/{id}` | **DELETE** | **删除FAQ**：仅限删除指定环境下的单条记录。 |
|  | `/api/v1/admin/faqs/status` | **PATCH** | **状态切换**：快速控制FAQ的启用或失效。 |


2. 对外服务模块 (Bot Service)

| 功能子模块 | 接口路径 (Endpoint) | 方法 | 描述 |
| --- | --- | --- | --- |
| **智能问答** | `/api/v1/service/ask` | **POST** | **语义检索**：多路召回正式环境中最匹配的答案。 |
| **关联推荐** | `/api/v1/service/recommend` | **GET** | **相关知识**：返回该问题关联的最多5条其他知识。 |

