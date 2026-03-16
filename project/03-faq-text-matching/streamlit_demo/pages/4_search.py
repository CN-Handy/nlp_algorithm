"""
FAQ System Demo - Search
搜索页面
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import api_client as api

st.set_page_config(page_title="搜索", page_icon="🔍")

st.title("🔍 搜索")


# Sidebar - Settings
with st.sidebar:
    st.header("设置")

    channel = st.selectbox(
        "选择渠道",
        ["default", "wechat", "app", "web"],
        index=0,
        format_func=lambda x: {
            "default": "默认",
            "wechat": "微信",
            "app": "App",
            "web": "网页"
        }.get(x, x)
    )

    limit = st.slider("返回数量", 1, 50, 10)


# Tab layout
tab1, tab2 = st.tabs(["🔍 关键词搜索", "📁 目录导航"])


# Tab 1: Keyword Search
with tab1:
    st.markdown("""
    ## 关键词搜索

    通过关键词在正式环境(PROD)中搜索FAQ。
    """)

    search_query = st.text_input(
        "输入搜索关键词：",
        placeholder="例如：密码 订单 退款",
        key="search_input"
    )

    if st.button("🔍 搜索", type="primary", use_container_width=True):
        if not search_query.strip():
            st.warning("请输入搜索关键词")
        else:
            with st.spinner("搜索中..."):
                result = api.search_faqs(search_query, channel=channel, limit=limit)

                if result.get("code") == 200:
                    results = result.get("data", {}).get("results", [])

                    if results:
                        st.success(f"找到 {len(results)} 个结果")

                        for i, item in enumerate(results, 1):
                            with st.container():
                                st.markdown(f"### 📄 结果 {i}")

                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"**{item.get('title', 'N/A')}**")
                                with col2:
                                    score = item.get("score", 0)
                                    st.metric("相关度", f"{score:.2f}")

                                # Content preview
                                content = item.get("content", "")
                                if content:
                                    st.markdown("**内容预览：**")
                                    st.write(content[:200] + "..." if len(content) > 200 else content)

                                # Solution
                                solution = item.get("solution", {})
                                if solution:
                                    st.markdown("**答案：**")
                                    st.info(solution.get("content", "N/A"))

                                st.markdown("---")
                    else:
                        st.warning("未找到相关结果")
                else:
                    st.error(f"搜索失败: {result.get('msg', 'Unknown error')}")


# Tab 2: Navigation
with tab2:
    st.markdown("""
    ## 目录导航

    浏览正式环境(PROD)的类目结构，点击类目查看相关FAQ。
    """)

    if st.button("🔄 刷新目录"):
        st.rerun()

    # Get navigation
    result = api.get_navigation()

    if result.get("code") == 200:
        tree_data = result.get("data", [])

        if tree_data:
            def display_category(nodes, indent=0):
                for node in nodes:
                    with st.expander("  " * indent + f"📁 {node['name']}"):
                        # Get FAQs in this category
                        faq_result = api.get_faqs(env="PROD", category_id=node["id"])

                        if faq_result.get("code") == 200:
                            faqs = faq_result.get("data", {}).get("items", [])

                            if faqs:
                                for faq in faqs:
                                    st.markdown(f"- **{faq['title']}** (ID: {faq['id']})")

                                    # Show status badge
                                    if faq.get("status") == "ENABLE":
                                        st.caption(f"  ✅ 启用")
                                    else:
                                        st.caption(f"  ❌ 禁用")

                                    # Recommend
                                    rec_result = api.get_recommend(faq["id"], limit=3)
                                    if rec_result.get("code") == 200:
                                        rec_faqs = rec_result.get("data", {}).get("faqs", [])
                                        if rec_faqs:
                                            st.caption(f"  关联: {', '.join([r['title'][:20] for r in rec_faqs[:3]])}")
                            else:
                                st.caption("暂无FAQ")

                        # Display children
                        if node.get("children"):
                            display_category(node["children"], indent + 1)

            display_category(tree_data)
        else:
            st.info("暂无目录数据")
    else:
        st.error(f"获取目录失败: {result.get('msg', 'Unknown error')}")
