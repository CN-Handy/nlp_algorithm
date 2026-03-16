"""
Bot Service API Tests
对外服务模块 API 测试
"""
import pytest
import requests


class TestSmartQA:
    """智能问答测试"""

    def test_ask_question_default_channel(self, base_url, base_headers):
        """测试智能问答（默认渠道）"""
        payload = {
            "question": "我忘记密码了怎么办",
            "top_k": 3
        }
        response = requests.post(
            f"{base_url}/api/v1/service/ask",
            json=payload,
            headers=base_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "answers" in data["data"]

    def test_ask_question_wechat_channel(self, base_url, base_headers):
        """测试智能问答（微信渠道）"""
        payload = {
            "question": "如何修改绑定手机号",
            "channel": "wechat",
            "top_k": 3
        }
        response = requests.post(
            f"{base_url}/api/v1/service/ask",
            json=payload,
            headers=base_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "answers" in data["data"]

        # Verify wechat perspective answer is returned
        if data["data"]["answers"]:
            answer = data["data"]["answers"][0]
            assert "solution" in answer

    def test_ask_question_app_channel(self, base_url, base_headers):
        """测试智能问答（App渠道）"""
        payload = {
            "question": "订单在哪里查看",
            "channel": "app",
            "top_k": 5
        }
        response = requests.post(
            f"{base_url}/api/v1/service/ask",
            json=payload,
            headers=base_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_ask_question_web_channel(self, base_url, base_headers):
        """测试智能问答（网页渠道）"""
        payload = {
            "question": "如何联系客服",
            "channel": "web",
            "top_k": 3
        }
        response = requests.post(
            f"{base_url}/api/v1/service/ask",
            json=payload,
            headers=base_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_ask_question_empty_question(self, base_url, base_headers):
        """测试智能问答空问题"""
        payload = {
            "question": "",
            "top_k": 3
        }
        response = requests.post(
            f"{base_url}/api/v1/service/ask",
            json=payload,
            headers=base_headers
        )

        # Should return validation error
        assert response.status_code == 422

    def test_ask_question_no_match(self, base_url, base_headers):
        """测试智能问答无匹配结果"""
        payload = {
            "question": "这是一 个完全不相关的问题xyz123",
            "top_k": 3
        }
        response = requests.post(
            f"{base_url}/api/v1/service/ask",
            json=payload,
            headers=base_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # Should return empty answers
        assert data["data"]["answers"] == []


class TestNavigation:
    """自助导航测试"""

    def test_get_navigation_tree(self, base_url, base_headers):
        """测试获取导航目录"""
        response = requests.get(
            f"{base_url}/api/v1/service/nav",
            headers=base_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data


class TestFAQDetail:
    """FAQ 详情获取测试"""

    def test_get_faq_detail_by_id(self, base_url, base_headers):
        """测试根据 ID 获取 FAQ 详情"""
        faq_id = 1  # Assuming FAQ with ID 1 exists
        response = requests.get(
            f"{base_url}/api/v1/service/faq/{faq_id}",
            headers=base_headers
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["code"] == 200

    def test_get_faq_detail_not_found(self, base_url, base_headers):
        """测试获取不存在的 FAQ"""
        response = requests.get(
            f"{base_url}/api/v1/service/faq/99999",
            headers=base_headers
        )

        assert response.status_code == 404


class TestRecommend:
    """关联推荐测试"""

    def test_get_related_faqs(self, base_url, base_headers):
        """测试获取关联 FAQ"""
        faq_id = 1  # Assuming FAQ with ID 1 exists
        response = requests.get(
            f"{base_url}/api/v1/service/recommend",
            params={"faq_id": faq_id, "limit": 5},
            headers=base_headers
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["code"] == 200
            assert "data" in data

    def test_get_related_faqs_default_limit(self, base_url, base_headers):
        """测试获取关联 FAQ 默认限制"""
        faq_id = 1
        response = requests.get(
            f"{base_url}/api/v1/service/recommend",
            params={"faq_id": faq_id},
            headers=base_headers
        )

        assert response.status_code in [200, 404]

    def test_get_related_faqs_no_faq_id(self, base_url, base_headers):
        """测试不提供 faq_id"""
        response = requests.get(
            f"{base_url}/api/v1/service/recommend",
            headers=base_headers
        )

        assert response.status_code == 422


class TestServiceIntegration:
    """服务集成测试 - 完整流程"""

    @pytest.fixture(autouse=True)
    def setup_faq_in_prod(self, base_url, auth_headers):
        """Setup: Create FAQ in PROD for testing"""
        # Create category in PROD
        cat_payload = {
            "env": "PROD",
            "name": "集成测试类目",
            "level": 1,
            "creator": "test"
        }
        cat_response = requests.post(
            f"{base_url}/api/v1/admin/categories",
            json=cat_payload,
            headers=auth_headers
        )
        self.category_id = cat_response.json()["data"]["id"]

        # Create FAQ in PROD
        faq_payload = {
            "env": "PROD",
            "category_id": self.category_id,
            "title": "集成测试FAQ - 如何退货？",
            "similar_queries": ["退货流程", "如何申请退货"],
            "tags": ["售后", "退货"],
            "status": "ENABLE",
            "creator": "test"
        }
        faq_response = requests.post(
            f"{base_url}/api/v1/admin/faqs",
            json=faq_payload,
            headers=auth_headers
        )
        self.faq_id = faq_response.json()["data"]["id"]

        # Add solution
        sol_payload = {
            "env": "PROD",
            "perspective": "default",
            "answer_type": "TEXT",
            "content": "请在订单详情页点击「申请退货」",
            "is_default": True,
            "creator": "test"
        }
        requests.post(
            f"{base_url}/api/v1/admin/faqs/{self.faq_id}/solutions",
            json=sol_payload,
            headers=auth_headers
        )

    def test_full_qa_flow(self, base_url, base_headers):
        """测试完整问答流程"""
        # 1. Ask question
        ask_payload = {
            "question": "我想退货怎么操作",
            "channel": "default",
            "top_k": 3
        }
        ask_response = requests.post(
            f"{base_url}/api/v1/service/ask",
            json=ask_payload,
            headers=base_headers
        )

        assert ask_response.status_code == 200
        ask_data = ask_response.json()
        assert ask_data["code"] == 200

        # 2. Get navigation
        nav_response = requests.get(
            f"{base_url}/api/v1/service/nav",
            headers=base_headers
        )
        assert nav_response.status_code == 200

        # 3. Get FAQ detail
        detail_response = requests.get(
            f"{base_url}/api/v1/service/faq/{self.faq_id}",
            headers=base_headers
        )
        assert detail_response.status_code == 200

        # 4. Get recommendations
        recommend_response = requests.get(
            f"{base_url}/api/v1/service/recommend",
            params={"faq_id": self.faq_id},
            headers=base_headers
        )
        assert recommend_response.status_code == 200
