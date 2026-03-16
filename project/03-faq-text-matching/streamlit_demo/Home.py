"""
FAQ System Demo - Home
主页面
"""
import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="FAQ智能问答系统",
    page_icon="💬",
    layout="wide"
)


def main():
    st.title("💬 FAQ智能问答系统 Demo")
    st.markdown("---")

    # Welcome section
    st.markdown("""
    ## 欢迎使用 FAQ 智能问答系统

    这是一个基于 FastAPI + Elasticsearch + Embedding 的智能问答系统演示界面。

    ### 系统功能
    - 📁 **类目管理** - 管理FAQ分类目录
    - 📝 **FAQ管理** - 管理常见问题
    - 💬 **智能问答** - 基于语义理解的智能问答
    - 🔍 **关键词搜索** - 全文检索
    - 📤 **发布同步** - 测试环境到正式环境的同步
    """)

    st.markdown("---")

    # Quick links
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.page_link("pages/1_category.py", label="📁 类目管理", icon="📁")

    with col2:
        st.page_link("pages/2_faq.py", label="📝 FAQ管理", icon="📝")

    with col3:
        st.page_link("pages/3_qa.py", label="💬 智能问答", icon="💬")

    with col4:
        st.page_link("pages/4_search.py", label="🔍 搜索", icon="🔍")

    st.markdown("---")

    # System status
    st.subheader("📊 系统状态")

    try:
        import requests
        from config import BASE_URL

        # Check API health
        resp = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=2)
        if resp.status_code == 200:
            st.success("✅ API 服务运行正常")
        else:
            st.warning("⚠️ API 服务异常")
    except Exception as e:
        st.error(f"❌ 无法连接到 API 服务: {e}")
        st.info("请确保 API 服务正在运行 (默认: http://localhost:8000)")


if __name__ == "__main__":
    main()
