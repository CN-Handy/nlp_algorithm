"""
Category Management API Tests
类目管理 API 测试
"""
import pytest
import requests


class TestCategoryManagement:
    """类目管理测试"""

    def test_create_level1_category(self, base_url, auth_headers, created_category_ids):
        """测试创建一级类目"""
        payload = {
            "env": "TEST",
            "name": "账户管理",
            "level": 1,
            "creator": "admin"
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "账户管理"
        assert data["data"]["level"] == 1
        assert data["data"]["env"] == "TEST"

        # Store ID for cleanup
        created_category_ids.append(data["data"]["id"])

    def test_create_level2_category(self, base_url, auth_headers, created_category_ids):
        """测试创建二级类目"""
        # First create parent category
        parent_payload = {
            "env": "TEST",
            "name": "账户管理",
            "level": 1,
            "creator": "admin"
        }
        parent_response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=parent_payload,
            headers=auth_headers
        )
        parent_id = parent_response.json()["data"]["id"]
        created_category_ids.append(parent_id)

        # Create child category
        child_payload = {
            "env": "TEST",
            "name": "密码找回",
            "parent_id": parent_id,
            "level": 2,
            "creator": "admin"
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=child_payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "密码找回"
        assert data["data"]["level"] == 2
        assert data["data"]["parent_id"] == parent_id

        created_category_ids.append(data["data"]["id"])

    def test_get_category_tree(self, base_url, auth_headers):
        """测试获取类目树"""
        response = requests.get(
            f"{base_url}/api/v1/admin/categories/tree",
            params={"env": "TEST"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data

    def test_update_category(self, base_url, auth_headers, created_category_ids):
        """测试修改类目"""
        # Create category first
        payload = {
            "env": "TEST",
            "name": "测试类目",
            "level": 1,
            "creator": "admin"
        }
        create_response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=payload,
            headers=auth_headers
        )
        category_id = create_response.json()["data"]["id"]
        created_category_ids.append(category_id)

        # Update category
        update_payload = {
            "name": "测试类目-已修改",
            "modifier": "admin"
        }
        response = requests.put(
            f"{base_url}/api/v1/admin/categories/{category_id}",
            json=update_payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "测试类目-已修改"

    def test_delete_category_soft(self, base_url, auth_headers, created_category_ids):
        """测试软删除类目"""
        # Create category first
        payload = {
            "env": "TEST",
            "name": "待删除类目",
            "level": 1,
            "creator": "admin"
        }
        create_response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=payload,
            headers=auth_headers
        )
        category_id = create_response.json()["data"]["id"]

        # Delete category (soft delete)
        response = requests.delete(
            f"{base_url}/api/v1/admin/categories/{category_id}",
            params={"soft_delete": "true"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_delete_category_with_faqs_should_fail(self, base_url, auth_headers, created_category_ids):
        """测试删除有关联FAQ的类目应失败"""
        # Create category and FAQ
        cat_payload = {
            "env": "TEST",
            "name": "有FAQ的类目",
            "level": 1,
            "creator": "admin"
        }
        cat_response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=cat_payload,
            headers=auth_headers
        )
        category_id = cat_response.json()["data"]["id"]
        created_category_ids.append(category_id)

        # Create FAQ under this category
        faq_payload = {
            "env": "TEST",
            "category_id": category_id,
            "title": "测试FAQ",
            "creator": "admin"
        }
        requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=faq_payload,
            headers=auth_headers
        )

        # Try to delete category - should fail
        response = requests.delete(
            f"{base_url}/api/v1/admin/categories/{category_id}",
            headers=auth_headers
        )

        assert response.status_code in [400, 409]
        data = response.json()
        assert data["code"] in [400, 409]


class TestCategoryValidation:
    """类目验证测试"""

    def test_create_category_missing_required_fields(self, base_url, auth_headers):
        """测试创建类目缺少必填字段"""
        payload = {
            "env": "TEST"
            # missing name, level
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_category_invalid_env(self, base_url, auth_headers):
        """测试创建类目使用无效的环境标识"""
        payload = {
            "env": "INVALID",
            "name": "测试",
            "level": 1,
            "creator": "admin"
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 422
