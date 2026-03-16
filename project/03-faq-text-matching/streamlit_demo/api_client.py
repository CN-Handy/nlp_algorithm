"""
API Client
API 调用辅助函数
"""
import requests
from typing import Optional, List, Dict, Any
from config import BASE_URL, get_headers


# ============================================
# Categories API
# ============================================

def get_categories(env: str = "TEST", page: int = 1, page_size: int = 100) -> Dict:
    """获取类目列表"""
    url = f"{BASE_URL}/admin/categories"
    params = {"env": env, "page": page, "page_size": page_size}
    resp = requests.get(url, params=params, headers=get_headers())
    return resp.json()


def get_category_tree(env: str = "TEST") -> Dict:
    """获取类目树"""
    url = f"{BASE_URL}/admin/categories/tree"
    params = {"env": env}
    resp = requests.get(url, params=params, headers=get_headers())
    return resp.json()


def get_category(category_id: int) -> Dict:
    """获取类目详情"""
    url = f"{BASE_URL}/admin/categories/{category_id}"
    resp = requests.get(url, headers=get_headers())
    return resp.json()


def create_category(data: Dict) -> Dict:
    """创建类目"""
    url = f"{BASE_URL}/admin/categories"
    resp = requests.post(url, json=data, headers=get_headers())
    return resp.json()


def update_category(category_id: int, data: Dict) -> Dict:
    """更新类目"""
    url = f"{BASE_URL}/admin/categories/{category_id}"
    resp = requests.put(url, json=data, headers=get_headers())
    return resp.json()


def delete_category(category_id: int) -> Dict:
    """删除类目"""
    url = f"{BASE_URL}/admin/categories/{category_id}"
    resp = requests.delete(url, headers=get_headers())
    return resp.json()


# ============================================
# FAQs API
# ============================================

def get_faqs(env: str = "TEST", category_id: int = None, status: str = None,
              page: int = 1, page_size: int = 20) -> Dict:
    """获取FAQ列表"""
    url = f"{BASE_URL}/admin/faqs"
    params = {"env": env, "page": page, "page_size": page_size}
    if category_id:
        params["category_id"] = category_id
    if status:
        params["status"] = status
    resp = requests.get(url, params=params, headers=get_headers())
    return resp.json()


def get_faq(faq_id: int) -> Dict:
    """获取FAQ详情"""
    url = f"{BASE_URL}/admin/faqs/{faq_id}"
    resp = requests.get(url, headers=get_headers())
    return resp.json()


def create_faq(data: Dict) -> Dict:
    """创建FAQ"""
    url = f"{BASE_URL}/admin/faqs"
    print(data)
    resp = requests.post(url, json=data, headers=get_headers())
    return resp.json()


def update_faq(faq_id: int, data: Dict) -> Dict:
    """更新FAQ"""
    url = f"{BASE_URL}/admin/faqs/{faq_id}"
    print(data)
    resp = requests.put(url, json=data, headers=get_headers())
    return resp.json()


def delete_faq(faq_id: int, env: str = "TEST") -> Dict:
    """删除FAQ"""
    url = f"{BASE_URL}/admin/faqs/{faq_id}"
    params = {"env": env}
    resp = requests.delete(url, params=params, headers=get_headers())
    return resp.json()


def update_faq_status(faq_ids: List[int], status: str, modifier: str = "admin") -> Dict:
    """更新FAQ状态"""
    url = f"{BASE_URL}/admin/faqs/status"
    data = {"faq_ids": faq_ids, "status": status, "modifier": modifier}
    resp = requests.patch(url, json=data, headers=get_headers())
    return resp.json()


def get_faq_solutions(faq_id: int) -> Dict:
    """获取FAQ答案列表"""
    url = f"{BASE_URL}/admin/faqs/{faq_id}/solutions"
    resp = requests.get(url, headers=get_headers())
    return resp.json()


def create_solution(faq_id: int, data: Dict) -> Dict:
    """创建FAQ答案"""
    url = f"{BASE_URL}/admin/faqs/{faq_id}/solutions"
    print(data)
    resp = requests.post(url, json=data, headers=get_headers())
    return resp.json()


# ============================================
# Service API
# ============================================

def ask_question(question: str, channel: str = "default", top_k: int = 3) -> Dict:
    """智能问答"""
    url = f"{BASE_URL}/service/ask"
    data = {"question": question, "channel": channel, "top_k": top_k}
    print(data)
    resp = requests.post(url, json=data, headers=get_headers())
    return resp.json()


def get_navigation() -> Dict:
    """获取导航目录"""
    url = f"{BASE_URL}/service/nav"
    resp = requests.get(url, headers=get_headers())
    return resp.json()


def get_recommend(faq_id: int, limit: int = 5) -> Dict:
    """获取推荐"""
    url = f"{BASE_URL}/service/recommend"
    params = {"faq_id": faq_id, "limit": limit}
    resp = requests.get(url, params=params, headers=get_headers())
    return resp.json()


def search_faqs(q: str, channel: str = "default", limit: int = 10) -> Dict:
    """关键词搜索"""
    url = f"{BASE_URL}/service/search"
    params = {"q": q, "channel": channel, "limit": limit}
    resp = requests.get(url, params=params, headers=get_headers())
    return resp.json()


# ============================================
# Sync API
# ============================================

def sync_preview(operator: str = "admin") -> Dict:
    """预览同步"""
    url = f"{BASE_URL}/admin/sync/preview"
    data = {"sync_type": "INCREMENTAL", "operator": operator}
    resp = requests.post(url, json=data, headers=get_headers())
    return resp.json()


def sync_execute(operator: str = "admin") -> Dict:
    """执行同步"""
    url = f"{BASE_URL}/admin/sync/execute"
    data = {"sync_type": "INCREMENTAL", "operator": operator}
    resp = requests.post(url, json=data, headers=get_headers())
    return resp.json()


def get_sync_history(limit: int = 20) -> Dict:
    """同步历史"""
    url = f"{BASE_URL}/admin/sync/history"
    params = {"limit": limit}
    resp = requests.get(url, params=params, headers=get_headers())
    return resp.json()
