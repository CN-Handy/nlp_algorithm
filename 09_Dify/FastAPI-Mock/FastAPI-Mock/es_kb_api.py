from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="外部知识库检索 API",
    description="连接到 Elasticsearch 的外部知识库 API，用于 Dify 集成。",
    version="1.0.0"
)

API_KEY = "1024"

async def verify_api_key(authorization: str = Header(...)):
    """
    验证 Authorization 头中的 API-Key。
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": 1001,
                "error_msg": "无效的 Authorization 头格式。预期格式为 'Bearer <api-key>'"
            }
        )
    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": 1002,
                "error_msg": "授权失败。"
            }
        )
    return True

class RetrievalSetting(BaseModel):
    top_k: int = Field(5, description="检索结果的最大数量")
    score_threshold: float = Field(0.0, description="结果与查询相关性的分数限制，范围：0~1") # 示例为0.0，实际可根据需要调整

class Condition(BaseModel):
    name: List[str] = Field(..., description="需要筛选的 metadata 名称")
    comparison_operator: str = Field(..., description="比较操作符")
    value: Optional[Union[str, int, float, bool]] = Field(None, description="对比值") # 可选，当操作符为 empty/not empty/null/not null 时可省略

class MetadataCondition(BaseModel):
    logical_operator: str = Field("and", description="逻辑操作符，取值为 'and' 或 'or'")
    conditions: List[Condition] = Field(..., description="条件列表")

class RetrievalRequest(BaseModel):
    knowledge_id: str = Field(..., description="知识库唯一 ID", examples=["AAA-BBB-CCC"])
    query: str = Field(..., description="用户的查询", examples=["Dify 是什么？"])
    retrieval_setting: RetrievalSetting = Field(..., description="知识检索参数")
    metadata_condition: Optional[MetadataCondition] = Field(None, description="原数组筛选")

class RecordMetadata(BaseModel):
    path: Optional[str] = None
    description: Optional[str] = None
    # 允许其他任意元数据字段
    extra: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, dict):
            # 将字典中的已知字段提取出来
            path = value.pop('path', None)
            description = value.pop('description', None)
            # 剩余的键值对存储到 extra
            return cls(path=path, description=description, extra=value)
        raise ValueError(f"Expected dict, got {type(value)}")


class RetrievalRecord(BaseModel):
    content: str = Field(..., description="包含知识库中数据源的文本块")
    score: float = Field(..., description="结果与查询的相关性分数，范围：0~1")
    title: str = Field(..., description="文档标题")
    metadata: Optional[RecordMetadata] = Field(None, description="包含数据源中文档的元数据属性及其值")

class RetrievalResponse(BaseModel):
    records: List[RetrievalRecord] = Field(..., description="从知识库查询的记录列表")

def build_es_query(request: RetrievalRequest) -> Dict[str, Any]:
    """
    根据 RetrievalRequest 构建 Elasticsearch Query DSL。
    这是一个简化示例，你需要根据实际需求扩展它。
    """
    must_clauses = []
    filter_clauses = [] # For exact matches or range filters

    # 1. 处理主查询
    if request.query:
        # 使用 match 查询在 'content' 字段上进行全文搜索
        must_clauses.append({"match": {"content": request.query}})
        # 你可能还需要在这里考虑 IK Analyzer，确保你的ES索引已经配置了IK
        # 例如: {"match": {"chinese_text": request.query}} 如果你的字段名是 chinese_text

    # 2. 处理元数据筛选 (metadata_condition)
    if request.metadata_condition and request.metadata_condition.conditions:
        # 假设所有 metadata 都是关键字字段或可用于精确匹配
        meta_clauses = []
        for cond in request.metadata_condition.conditions:
            # 简化处理：假设 'name' 列表只有一个元素，并且直接映射到ES的元数据字段
            meta_field_name = f"metadata.{cond.name[0]}.keyword" # 假设元数据是 keyword 类型

            if cond.comparison_operator == "contains":
                meta_clauses.append({"match_phrase": {meta_field_name: cond.value}})
            elif cond.comparison_operator == "is":
                meta_clauses.append({"term": {meta_field_name: cond.value}})
            elif cond.comparison_operator == "is not":
                meta_clauses.append({"bool": {"must_not": {"term": {meta_field_name: cond.value}}}})
            elif cond.comparison_operator == "empty":
                meta_clauses.append({"bool": {"must_not": {"exists": {"field": meta_field_name}}}})
            elif cond.comparison_operator == "not empty":
                meta_clauses.append({"exists": {"field": meta_field_name}})
            # 可以根据需要添加更多操作符的映射
            elif cond.comparison_operator in ["=", "≠", ">", "<", "≥", "≤", "before", "after"]:
                # 对于数值或日期操作符，你可能需要转换为 range 查询
                # 例如: {"range": {meta_field_name: {"gte": cond.value}}}
                print(f"Warning: Operator '{cond.comparison_operator}' for metadata not fully implemented in this example.")
                pass
            else:
                print(f"Warning: Unsupported comparison_operator: {cond.comparison_operator}")

        if meta_clauses:
            if request.metadata_condition.logical_operator == "and":
                filter_clauses.extend(meta_clauses)
            else: # or
                filter_clauses.append({"bool": {"should": meta_clauses, "minimum_should_match": 1}})

    query_body = {
        "query": {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses
            }
        },
        "size": request.retrieval_setting.top_k,
        "min_score": request.retrieval_setting.score_threshold
    }
    return query_body

# --- API 端点 ---

@app.post("/retrieval", response_model=RetrievalResponse)
async def retrieval(
    request_body: RetrievalRequest,
    api_key_valid: bool = Depends(verify_api_key) # 使用依赖注入进行API密钥验证
):
    """
    处理外部知识库的检索请求。
    """
    # 理论上这里的 knowledge_id 可以用于选择不同的 Elasticsearch 索引
    # 或在同一个索引中根据 knowledge_id 字段进行过滤
    # 这里我们简化，直接使用 knowledge_id 作为 Elasticsearch 索引名
    es_index_name = request_body.knowledge_id.lower() # 通常索引名是小写的

    try:
        # 构建 Elasticsearch 查询体
        es_query_body = build_es_query(request_body)

        # 执行 Elasticsearch 搜索
        # 对外部数据的哪一个库、以什么逻辑进行检索
        es_response = es.search(
            index=es_index_name,
            body=es_query_body,
            size=request_body.retrieval_setting.top_k,
            min_score=request_body.retrieval_setting.score_threshold
        )

        # 格式化 Elasticsearch 响应为 Dify 期望的格式
        records: List[RetrievalRecord] = []
        for hit in es_response['hits']['hits']:
            # 假设你的ES文档结构是 { "content": "...", "title": "...", "metadata": {...} }
            source = hit['_source']
            record_metadata = None
            if 'metadata' in source and isinstance(source['metadata'], dict):
                # 将ES元数据中的所有键值对传递给 RecordMetadata，以便它处理 'extra'
                record_metadata = RecordMetadata(**source['metadata'])
            
            # 确保 content, title, score 存在
            content = source.get('content', '')
            title = source.get('title', '无标题')
            score = hit['_score'] if hit['_score'] is not None else 0.0 # score可能为null

            records.append(
                RetrievalRecord(
                    content=content,
                    score=score,
                    title=title,
                    metadata=record_metadata
                )
            )

        return RetrievalResponse(records=records)

    except Exception as e:
        # 记录详细错误，但对客户端返回通用错误
        print(f"处理检索请求时发生内部错误: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 5000, # 自定义错误码
                "error_msg": "内部服务器错误。"
            }
        )

# --- 根路径用于健康检查 (可选) ---
@app.get("/")
async def read_root():
    return {"message": "External Knowledge Base API is running."}

# uvicorn main:app --reload