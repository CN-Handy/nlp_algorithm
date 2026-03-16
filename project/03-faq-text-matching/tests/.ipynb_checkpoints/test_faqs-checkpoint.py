"""
FAQ Core API Tests
FAQ 核心 API 测试
"""
import pytest
import requests


class TestFAQManagement:
    """FAQ 管理测试"""

    @pytest.fixture(autouse=True)
    def setup_category(self, base_url, auth_headers):
        """创建测试用类目"""
        payload = {
            "env": "TEST",
            "name": "测试类目",
            "level": 1,
            "creator": "admin"
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=payload,
            headers=auth_headers
        )
        self.category_id = response.json()["data"]["id"]

    def test_create_faq(self, base_url, auth_headers, created_faq_ids):
        """测试创建 FAQ"""
        payload = {
            "env": "TEST",
            "category_id": self.category_id,
            "title": "如何找回登录密码？",
            "similar_queries": ["忘记密码怎么办", "密码丢失如何处理", "密码重置方法"],
            "related_ids": [],
            "tags": ["账户", "密码", "安全"],
            "status": "ENABLE",
            "is_permanent": True,
            "creator": "admin"
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["title"] == "如何找回登录密码？"
        assert data["data"]["category_id"] == self.category_id

        created_faq_ids.append(data["data"]["id"])

    def test_create_faq_with_solutions(self, base_url, auth_headers, created_faq_ids):
        """测试创建 FAQ 并添加答案"""
        # Create FAQ
        faq_payload = {
            "env": "TEST",
            "category_id": self.category_id,
            "title": "如何修改绑定手机号？",
            "similar_queries": ["手机号更换", "更换手机绑定"],
            "tags": ["账户", "手机"],
            "status": "ENABLE",
            "creator": "admin"
        }
        faq_response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=faq_payload,
            headers=auth_headers
        )
        faq_id = faq_response.json()["data"]["id"]
        created_faq_ids.append(faq_id)

        # Add default solution
        solution_payload = {
            "env": "TEST",
            "perspective": "default",
            "answer_type": "TEXT",
            "content": "请前往「我的」-「账户安全」-「修改手机号」进行操作",
            "is_default": True,
            "creator": "admin"
        }
        solution_response = requests.post(
            f"{base_url}/api/v1/admin/faqs/{faq_id}/solutions",
            json=solution_payload,
            headers=auth_headers
        )

        assert solution_response.status_code == 200
        assert solution_response.json()["code"] == 200

    def test_create_faq_with_multi_perspective(self, base_url, auth_headers, created_faq_ids):
        """测试创建多视角答案的 FAQ"""
        # Create FAQ
        faq_payload = {
            "env": "TEST",
            "category_id": self.category_id,
            "title": "如何查询订单？",
            "tags": ["订单"],
            "creator": "admin"
        }
        faq_response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=faq_payload,
            headers=auth_headers
        )
        faq_id = faq_response.json()["data"]["id"]
        created_faq_ids.append(faq_id)

        # Add default solution
        default_payload = {
            "env": "TEST",
            "perspective": "default",
            "answer_type": "TEXT",
            "content": "请在订单页面查看",
            "is_default": True,
            "creator": "admin"
        }
        requests.post(
            f"{base_url}/api/v1/admin/faqs/{faq_id}/solutions",
            json=default_payload,
            headers=auth_headers
        )

        # Add wechat perspective solution
        wechat_payload = {
            "env": "TEST",
            "perspective": "wechat",
            "answer_type": "RICH",
            "content": '{"type":"rich","text":"请在微信小程序-我的订单中查看"}',
            "is_default": False,
            "creator": "admin"
        }
        wechat_response = requests.post(
            f"{base_url}/api/v1/admin/faqs/{faq_id}/solutions",
            json=wechat_payload,
            headers=auth_headers
        )

        assert wechat_response.status_code == 200
        data = wechat_response.json()
        assert data["data"]["perspective"] == "wechat"

    def test_update_faq(self, base_url, auth_headers, created_faq_ids):
        """测试修改 FAQ"""
        # Create FAQ first
        create_payload = {
            "env": "TEST",
            "category_id": self.category_id,
            "title": "原标题",
            "creator": "admin"
        }
        create_response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=create_payload,
            headers=auth_headers
        )
        faq_id = create_response.json()["data"]["id"]
        created_faq_ids.append(faq_id)

        # Update FAQ
        update_payload = {
            "title": "新标题",
            "similar_queries": ["新相似问法"],
            "related_ids": [],
            "tags": ["新标签"],
            "modifier": "admin"
        }
        response = requests.put(
            f"{base_url}/api/v1/admin/faqs/{faq_id}",
            json=update_payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["title"] == "新标题"

    def test_update_faq_status(self, base_url, auth_headers, created_faq_ids):
        """测试切换 FAQ 状态"""
        # Create FAQ
        create_payload = {
            "env": "TEST",
            "category_id": self.category_id,
            "title": "状态测试FAQ",
            "status": "ENABLE",
            "creator": "admin"
        }
        create_response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=create_payload,
            headers=auth_headers
        )
        faq_id = create_response.json()["data"]["id"]
        created_faq_ids.append(faq_id)

        # Disable FAQ
        status_payload = {
            "faq_ids": [faq_id],
            "status": "DISABLE",
            "modifier": "admin"
        }
        response = requests.patch(
            f"{base_url}/api/v1/admin/faqs/status",
            json=status_payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_delete_faq(self, base_url, auth_headers, created_faq_ids):
        """测试删除 FAQ"""
        # Create FAQ
        create_payload = {
            "env": "TEST",
            "category_id": self.category_id,
            "title": "待删除FAQ",
            "creator": "admin"
        }
        create_response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=create_payload,
            headers=auth_headers
        )
        faq_id = create_response.json()["data"]["id"]

        # Delete FAQ
        response = requests.delete(
            f"{base_url}/api/v1/admin/faqs/{faq_id}",
            params={"env": "TEST"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestFAQBatch:
    """FAQ 批量操作测试"""

    @pytest.fixture(autouse=True)
    def setup_category(self, base_url, auth_headers):
        """创建测试用类目"""
        payload = {
            "env": "TEST",
            "name": "批量测试类目",
            "level": 1,
            "creator": "admin"
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=payload,
            headers=auth_headers
        )
        self.category_id = response.json()["data"]["id"]

    def test_batch_import_faqs(self, base_url, auth_headers):
        """测试批量导入 FAQ"""
        payload = {
            "action": "import",
            "env": "TEST",
            "data": [
                {
                    "category_id": self.category_id,
                    "title": "批量导入FAQ标题1",
                    "similar_queries": ["相似问1", "相似问2"],
                    "tags": ["标签1"],
                    "solutions": [
                        {
                            "perspective": "default",
                            "answer_type": "TEXT",
                            "content": "答案内容1"
                        }
                    ]
                },
                {
                    "category_id": self.category_id,
                    "title": "批量导入FAQ标题2",
                    "similar_queries": ["相似问3"],
                    "tags": ["标签2"],
                    "solutions": [
                        {
                            "perspective": "default",
                            "answer_type": "TEXT",
                            "content": "答案内容2"
                        }
                    ]
                }
            ]
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/faqs/batch",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_batch_export_faqs(self, base_url, auth_headers):
        """测试批量导出 FAQ"""
        payload = {
            "action": "export",
            "env": "TEST",
            "category_id": self.category_id,
            "limit": 1000
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/faqs/batch",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data


class TestFAQValidation:
    """FAQ 验证测试"""

    def test_create_faq_missing_required_fields(self, base_url, auth_headers):
        """测试创建 FAQ 缺少必填字段"""
        payload = {
            "env": "TEST"
            # missing category_id, title
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_faq_invalid_category(self, base_url, auth_headers):
        """测试创建 FAQ 使用不存在的类目"""
        payload = {
            "env": "TEST",
            "category_id": 99999,
            "title": "测试FAQ",
            "creator": "admin"
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code in [400, 404]

    def test_create_faq_invalid_status(self, base_url, auth_headers):
        """测试创建 FAQ 使用无效状态"""
        payload = {
            "env": "TEST",
            "category_id": 1,
            "title": "测试FAQ",
            "status": "INVALID_STATUS",
            "creator": "admin"
        }
        response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 422
