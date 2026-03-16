#!/usr/bin/env python
"""
Environment Test Script
环境测试脚本 - 测试中间件连接
"""
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, List, Tuple

# 添加项目根目录到 path
sys.path.insert(0, "./")

from app.config import settings

# ============================================
# Test Results
# ============================================

class TestResult:
    def __init__(self, name: str, status: bool, message: str = "", latency_ms: float = 0):
        self.name = name
        self.status = status
        self.message = message
        self.latency_ms = latency_ms

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": "OK" if self.status else "FAIL",
            "message": self.message,
            "latency_ms": round(self.latency_ms, 2)
        }


# ============================================
# Test Functions
# ============================================

def test_mysql() -> TestResult:
    """测试 MySQL 连接"""
    name = "MySQL"
    start_time = time.time()

    try:
        import pymysql

        conn = pymysql.connect(
            host=settings.database.mysql.host,
            port=settings.database.mysql.port,
            user=settings.database.mysql.user,
            password=settings.database.mysql.password,
            db=settings.database.mysql.database,
            charset=settings.database.mysql.charset,
            connect_timeout=5,
        )

        # 执行简单查询
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()

        conn.close()

        latency_ms = (time.time() - start_time) * 1000
        return TestResult(
            name=name,
            status=True,
            message=f"Connected - Version: {version[0]}",
            latency_ms=latency_ms
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        traceback.print_exc()
        return TestResult(
            name=name,
            status=False,
            message=f"Connection failed: {str(e)}",
            latency_ms=latency_ms
        )


def test_elasticsearch() -> TestResult:
    """测试 Elasticsearch 连接"""
    name = "Elasticsearch"
    start_time = time.time()

    try:
        from elasticsearch import Elasticsearch

        client = Elasticsearch(
            hosts=settings.elasticsearch.hosts,
            timeout=5,
            max_retries=1,
        )

        # 获取集群信息
        info = client.info()
        cluster_name = info.get("cluster_name", "unknown")
        version = info.get("version", {}).get("number", "unknown")

        client.close()

        latency_ms = (time.time() - start_time) * 1000
        return TestResult(
            name=name,
            status=True,
            message=f"Connected - Cluster: {cluster_name}, Version: {version}",
            latency_ms=latency_ms
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return TestResult(
            name=name,
            status=False,
            message=f"Connection failed: {str(e)}",
            latency_ms=latency_ms
        )


def test_elasticsearch_vector() -> TestResult:
    """测试 Elasticsearch 向量搜索支持"""
    name = "ES Vector Support"
    start_time = time.time()

    try:
        from elasticsearch import Elasticsearch

        client = Elasticsearch(
            hosts=settings.elasticsearch.hosts,
            timeout=5,
        )

        # 检查 ES 版本是否支持向量 (8.x+)
        info = client.info()
        version = info.get("version", {}).get("number", "0.0.0")
        major_version = int(version.split(".")[0])

        if major_version >= 8:
            message = f"ES {version} supports dense_vector"
            status = True
        else:
            message = f"ES {version} does not support dense_vector (need 8.x+)"
            status = False

        client.close()

        latency_ms = (time.time() - start_time) * 1000
        return TestResult(
            name=name,
            status=status,
            message=message,
            latency_ms=latency_ms
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return TestResult(
            name=name,
            status=False,
            message=f"Check failed: {str(e)}",
            latency_ms=latency_ms
        )


def test_embedding() -> TestResult:
    """测试 Embedding 模型"""
    name = "Embedding Model"
    start_time = time.time()

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(
            settings.embedding.local.model_name,
            device=settings.embedding.local.device
        )

        # 测试编码
        test_texts = ["这是一个测试句子", "This is a test sentence"]
        embeddings = model.encode(
            test_texts,
            normalize_embeddings=settings.embedding.local.normalize_embeddings,
            show_progress_bar=False
        )

        dimension = embeddings.shape[1]
        latency_ms = (time.time() - start_time) * 1000

        return TestResult(
            name=name,
            status=True,
            message=f"Model: {settings.embedding.local.model_name}, Dimension: {dimension}, Device: {settings.embedding.local.device}",
            latency_ms=latency_ms
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return TestResult(
            name=name,
            status=False,
            message=f"Failed: {str(e)}",
            latency_ms=latency_ms
        )


def print_result(results: List[TestResult]):
    """打印测试结果"""
    print("\n" + "=" * 60)
    print(f"Environment Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 打印配置信息
    print("\n[Configuration]")
    print(f"  MySQL:   {settings.database.mysql.host}:{settings.database.mysql.port}/{settings.database.mysql.database}")
    print(f"  ES:      {settings.elasticsearch.hosts}")
    print(f"  Embedding: {settings.embedding.provider} - {settings.embedding.local.model_name} ({settings.embedding.local.device})")

    # 打印测试结果
    print("\n[Test Results]")
    print("-" * 60)
    print(f"{'Service':<25} {'Status':<8} {'Latency':<12} {'Message'}")
    print("-" * 60)

    success_count = 0
    for result in results:
        status_str = "✓ OK" if result.status else "✗ FAIL"
        if result.status:
            success_count += 1

        latency_str = f"{result.latency_ms:.2f}ms" if result.latency_ms > 0 else "-"
        message = result.message[:30] + "..." if len(result.message) > 30 else result.message

        print(f"{result.name:<25} {status_str:<8} {latency_str:<12} {message}")

    print("-" * 60)
    print(f"\nSummary: {success_count}/{len(results)} tests passed")

    # 返回状态码
    return 0 if success_count == len(results) else 1


def main():
    """主函数"""
    print("\nStarting environment tests...")

    # 运行所有测试
    results: List[TestResult] = []

    # 顺序执行测试
    results.append(test_mysql())
    results.append(test_embedding())

    # 打印结果并返回状态码
    return print_result(results)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
