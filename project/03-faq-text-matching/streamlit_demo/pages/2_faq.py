"""
FAQ System Demo - FAQ Management
FAQ管理页面
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import api_client as api
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="FAQ管理", page_icon="📝")

st.title("📝 FAQ管理")


# Sidebar - Environment selection
with st.sidebar:
    st.header("环境选择")
    env = st.selectbox("选择环境", ["TEST", "PROD"], index=0)


# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["📋 FAQ列表", "➕ 新建FAQ", "💬 管理答案", "🔄 批量操作"])


# Tab 1: FAQ List
with tab1:
    st.subheader("FAQ列表")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.number_input("类目ID(可选)", min_value=1, step=1)
    with col2:
        status_filter = st.selectbox("状态(可选)", ["", "ENABLE", "DISABLE"])
    with col3:
        if st.button("🔄 刷新"):
            st.rerun()

    # Get FAQs
    kwargs = {"env": env}
    if category_filter:
        kwargs["category_id"] = category_filter
    if status_filter:
        kwargs["status"] = status_filter

    result = api.get_faqs(**kwargs)

    if result.get("code") == 200:
        data = result.get("data", {})
        items = data.get("items", [])

        if items:
            # Display as table
            df = pd.DataFrame(items)
            st.dataframe(
                df[["id", "title", "category_id", "status", "tags", "creator", "created_at"]],
                use_container_width=True,
                hide_index=True
            )

            # FAQ actions
            st.subheader("操作")
            col1, col2 = st.columns(2)

            with col1:
                faq_id = st.number_input("输入FAQ ID", min_value=1, step=1, key=1)

            with col2:
                if st.button("查看详情"):
                    detail = api.get_faq(int(faq_id))
                    if detail.get("code") == 200:
                        st.json(detail.get("data"))
                    else:
                        st.error(detail.get("msg", "获取失败"))
        else:
            st.info("暂无FAQ数据")
    else:
        st.error(result.get("msg", "获取失败"))


# Tab 2: Create FAQ
with tab2:
    st.subheader("创建新FAQ")

    # Get categories
    cat_result = api.get_categories(env=env)
    categories = cat_result.get("data", {}).get("items", []) if cat_result.get("code") == 200 else []

    with st.form("create_faq_form"):
        title = st.text_input("标题", max_chars=255)
        category_id = st.selectbox("类目", options=[c["id"] for c in categories], format_func=lambda x: next((c["name"] for c in categories if c["id"] == x), ""))

        similar_queries = st.text_area("相似问(每行一个)", height=100)
        tags = st.text_input("标签(逗号分隔)")

        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("状态", ["ENABLE", "DISABLE"])
        with col2:
            is_permanent = st.checkbox("永久生效", value=True)

        creator = st.text_input("创建人", value="admin")

        submitted = st.form_submit_button("创建", type="primary")

        if submitted:
            if not title or not category_id:
                st.error("请填写必要字段")
            else:
                data = {
                    "env": env,
                    "title": title,
                    "category_id": category_id,
                    "similar_queries": [q.strip() for q in similar_queries.split("\n") if q.strip()],
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "status": status,
                    "is_permanent": is_permanent,
                    "creator": creator
                }

                result = api.create_faq(data)
                if result.get("code") == 201:
                    st.success("创建成功!")
                    st.json(result.get("data"))
                else:
                    st.error(result.get("msg", "创建失败"))


# Tab 3: Manage Solutions
with tab3:
    st.subheader("管理答案")

    faq_id = st.number_input("输入FAQ ID", min_value=1, step=1, key=2)

    if st.button("加载答案"):
        # Get FAQ details
        faq_detail = api.get_faq(int(faq_id))
        if faq_detail.get("code") == 200:
            st.json(faq_detail.get("data"))
        else:
            st.error(faq_detail.get("msg", "获取失败"))

        # Get solutions
        sol_result = api.get_faq_solutions(int(faq_id))
        if sol_result.get("code") == 200:
            solutions = sol_result.get("data", {}).get("items", [])
            if solutions:
                st.write("### 已有答案")
                for sol in solutions:
                    st.write(f"- **{sol['perspective']}** ({sol['answer_type']}): {sol['content'][:100]}...")
            else:
                st.info("暂无答案")

    st.markdown("---")

    # Add solution
    st.write("### 添加答案")

    with st.form("add_solution_form"):
        faq_id = st.number_input("输入FAQ ID", min_value=1, step=1, key=3)
        perspective = st.text_input("视角(default/wechat/app/web)", value="default")
        answer_type = st.selectbox("答案类型", ["TEXT", "RICH", "CARD"])
        content = st.text_area("答案内容", height=150)
        is_default = st.checkbox("设为默认答案", value=True)
        creator = st.text_input("创建人", value="admin")

        submitted = st.form_submit_button("添加答案", type="primary")

        if submitted:
            if not content:
                st.error("请填写答案内容")
            else:
                data = {
                    "faq_id": int(faq_id),
                    "env": env,
                    "perspective": perspective,
                    "answer_type": answer_type,
                    "content": content,
                    "is_default": is_default,
                    "creator": creator
                }

                result = api.create_solution(int(faq_id), data)
                if result.get("code") == 201:
                    st.success("添加成功!")
                    st.rerun()
                else:
                    st.error(result.get("msg", "添加失败"))


# Tab 4: Batch Operations
with tab4:
    st.subheader("批量操作")

    # Update status
    st.write("### 批量更新状态")

    col1, col2 = st.columns(2)
    with col1:
        faq_ids_str = st.text_area("FAQ ID列表(逗号分隔)")
    with col2:
        new_status = st.selectbox("新状态", ["ENABLE", "DISABLE"])

    if st.button("批量更新状态", type="primary"):
        if faq_ids_str:
            faq_ids = [int(x.strip()) for x in faq_ids_str.split(",") if x.strip()]
            result = api.update_faq_status(faq_ids, new_status)
            if result.get("code") == 200:
                st.success(f"更新成功! 影响 {result.get('data', {}).get('updated_count', 0)} 条")
            else:
                st.error(result.get("msg", "更新失败"))
        else:
            st.error("请输入FAQ ID")

    st.markdown("---")

    # Delete FAQ
    st.write("### 删除FAQ")

    delete_id = st.number_input("输入要删除的FAQ ID", min_value=1, step=1)

    if st.button("确认删除", type="primary"):
        result = api.delete_faq(int(delete_id), env=env)
        if result.get("code") == 204:
            st.success("删除成功!")
            st.rerun()
        else:
            st.error(result.get("msg", "删除失败"))
