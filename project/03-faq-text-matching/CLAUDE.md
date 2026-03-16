# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Customer Service Workstation & AI-FAQ System** built with Python async ecosystem. It provides multi-channel integration, dual-environment FAQ management (TEST/PROD), intelligent semantic search (ES + Embedding), and an agent workstation.

## Core Architecture

- **Framework**: FastAPI (async ASGI)
- **Database**: MySQL + SQLAlchemy 2.0 (async driver: aiomysql)
- **Cache**: Redis (multi-level caching)
- **Search**: Elasticsearch 8.x (Full-text + Vector search with dense_vector)
- **Embedding**: Sentence-Transformers (local model for semantic search)
- **Logging**: Loguru (level-based, time-rotated, 14-day retention)

## Key Concepts

1. **Dual Environment Isolation**: TEST → SIMULATE → PUBLISH → PROD workflow
2. **Multi-perspective Answers**: Same question can have different answers per channel
3. **Hybrid Search**: ES keyword + vector search with RRF fusion
4. **Multi-level Cache**: Redis caching for categories, FAQs, search results

## Database Structure

### Tables
- `categories` - 类目管理 (TEST/PROD, 2-level hierarchy)
- `faqs` - FAQ 主表 (支持时间有效性)
- `faq_solutions` - FAQ 答案 (多视角: default/wechat/app/web)
- `channels` - 渠道配置
- `sync_records` - 发布同步记录
- `faq_versions` - FAQ 版本历史

## Project Structure

```
.
├── config.yaml              # 应用配置文件
├── .env.example            # 环境变量模板
├── requirements.txt        # 项目依赖
├── logs/                   # 日志目录
├── scripts/                # 工具脚本
│   ├── test_env.py        # 环境测试脚本
│   └── README.md
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用入口
│   ├── config.py          # 配置加载 (Pydantic)
│   ├── database.py        # 异步数据库连接
│   ├── models.py          # SQLAlchemy ORM 模型
│   ├── datamodels.py     # Pydantic 数据模型 (统一)
│   ├── exceptions.py      # 统一响应工具函数
│   ├── cache.py           # Redis 缓存模块
│   ├── logging_config.py # 日志配置
│   ├── middleware/        # 中间件
│   │   ├── __init__.py
│   │   └── logging.py    # 请求/响应日志中间件
│   ├── routers/           # API 路由
│   │   ├── __init__.py
│   │   ├── categories.py # 类目管理
│   │   ├── faqs.py      # FAQ 管理
│   │   ├── service.py    # 对外服务
│   │   └── sync.py      # 发布同步
│   └── services/          # 业务服务
│       ├── __init__.py
│       ├── elasticsearch.py  # ES 搜索服务
│       └── embedding.py      # 向量生成服务
└── tests/                 # HTTP 测试用例
```

## Key Files

| File | Description |
|------|-------------|
| `config.yaml` | 主配置文件 (MySQL, Redis, ES, Embedding) |
| `app/main.py` | FastAPI 应用入口，包含生命周期管理、ES索引初始化 |
| `app/database.py` | 异步数据库连接和会话管理 |
| `app/models.py` | SQLAlchemy ORM 模型 (6张表) |
| `app/datamodels.py` | Pydantic 数据模型 (统一，包含 Enum、Request/Response) |
| `app/exceptions.py` | 统一响应工具函数 (success, not_found, bad_request 等) |
| `app/cache.py` | Redis 缓存模块 (@cached 装饰器, 缓存管理) |
| `app/auth.py` | JWT 认证模块 (token 创建/验证, 角色权限) |
| `app/logging_config.py` | 日志配置 (按级别分文件, 时间滚动, 14天保留) |
| `app/middleware/logging.py` | 请求/响应日志中间件 (记录 IP, 请求体大小限制, 响应, 异常) |
| `app/services/elasticsearch.py` | ES 搜索服务 (关键词/向量/混合搜索) |
| `app/services/embedding.py` | 向量生成服务 (Sentence-Transformers) |

## API Endpoints

### Admin APIs (Knowledge Management)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/admin/categories` | 创建类目 |
| GET | `/api/v1/admin/categories` | 获取类目列表 |
| GET | `/api/v1/admin/categories/tree` | 获取类目树 |
| GET | `/api/v1/admin/categories/{id}` | 获取类目详情 |
| PUT | `/api/v1/admin/categories/{id}` | 更新类目 |
| DELETE | `/api/v1/admin/categories/{id}` | 删除类目 |
| POST | `/api/v1/admin/faqs` | 创建 FAQ |
| GET | `/api/v1/admin/faqs` | 获取 FAQ 列表 |
| GET | `/api/v1/admin/faqs/{id}` | 获取 FAQ 详情 |
| PUT | `/api/v1/admin/faqs/{id}` | 更新 FAQ |
| PATCH | `/api/v1/admin/faqs/status` | 批量更新状态 |
| DELETE | `/api/v1/admin/faqs/{id}` | 删除 FAQ |
| POST | `/api/v1/admin/faqs/{id}/solutions` | 添加答案 |
| GET | `/api/v1/admin/faqs/{id}/solutions` | 获取答案列表 |
| GET | `/api/v1/admin/faqs/{id}/versions` | 版本历史 |
| POST | `/api/v1/admin/faqs/reindex` | 重建索引 |
| POST | `/api/v1/admin/faqs/{id}/index` | 索引单个 FAQ |
| DELETE | `/api/v1/admin/faqs/{id}/index` | 删除索引 |
| POST | `/api/v1/admin/sync/preview` | 预览同步差异 |
| POST | `/api/v1/admin/sync/execute` | 执行同步 |
| GET | `/api/v1/admin/sync/history` | 同步历史 |

### Service APIs (Bot Service)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/service/ask` | 智能问答 (混合搜索) |
| GET | `/api/v1/service/search` | 关键词搜索 |
| GET | `/api/v1/service/nav` | 自助导航 |
| GET | `/api/v1/service/faq/{id}` | FAQ 详情 |
| GET | `/api/v1/service/recommend` | 关联推荐 |
| GET | `/api/v1/service/stats` | 系统统计 |

## Response Format

All API responses follow a unified format:

```json
{
  "code": 200,
  "msg": "success",
  "data": {},
  "time": "2024-01-01T00:00:00"
}
```

| Field | Type | Description |
|-------|------|-------------|
| code | int | Status code (200=success, 201=created, 400=bad request, 404=not found, 500=error) |
| msg | string | Response message |
| data | any | Response data |
| time | datetime | Timestamp |

Use `app/exceptions.py` helper functions:
- `success(data, msg)` - Success response
- `created(data, msg)` - Created response
- `no_content(msg)` - No content response
- `not_found(msg)` - Not found response
- `bad_request(msg)` - Bad request response
- `server_error(msg)` - Server error response

## Logging

- Console: Colored output for all levels
- Files: Separate files by level (`debug_`, `info_`, `warning_`, `error_`, `critical_`, `access_`)
- Rotation: Daily rotation
- Retention: 14 days
- Request logging: IP, method, path, params, body, response, duration, exceptions

## Development Notes

- Use async SQLAlchemy 2.0 patterns with aiomysql
- Follow dual-environment design (TEST/PROD) for all database operations
- Use Pydantic for data validation (datamodels.py)
- Use `app/cache.py` decorators for caching (`@cached`, `@invalidate_cache`)
- Use `app/exceptions.py` for consistent API responses
- Configuration loaded from config.yaml with environment variable overrides
