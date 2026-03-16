"""
FAQ System Demo - Category Management
类目管理页面
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import api_client as api
import pandas as pd

st.set_page_config(page_title="类目管理", page_icon="📁")

st.title("📁 类目管理")


# Sidebar - Environment selection
with st.sidebar:
    st.header("环境选择")
    env = st.selectbox("选择环境", ["TEST", "PROD"], index=0)


# Tab layout
tab1, tab2, tab3 = st.tabs(["📋 类目列表", "🌳 类目树", "➕ 新建类目"])


# Tab 1: Category List
with tab1:
    st.subheader("类目列表")

    if st.button("🔄 刷新列表"):
        st.rerun()

    # Get categories
    result = api.get_categories(env=env)

    if result.get("code") == 200 and result.get("data"):
        data = result["data"]
        items = data.get("items", [])

        if items:
            # Display as table
            df = pd.DataFrame(items)
            st.dataframe(
                df[["id", "name", "level", "parent_id", "creator", "created_at"]],
                use_container_width=True
            )

            # Category actions
            st.subheader("操作")
            col1, col2 = st.columns(2)

            with col1:
                category_id = st.number_input("输入类目ID", min_value=1, step=1)

            with col2:
                if st.button("查看详情"):
                    detail = api.get_category(int(category_id))
                    if detail.get("code") == 200:
                        st.json(detail.get("data"))
                    else:
                        st.error(detail.get("msg", "获取失败"))

            # Delete category
            with st.expander("🗑️ 删除类目"):
                delete_id = st.number_input("输入要删除的类目ID", min_value=1, step=1)
                if st.button("确认删除", type="primary = api.delete_category(int(delete_id))
"):
                    result                    if result.get("code") == 204:
                        st.success("删除成功")
                        st.rerun()
                    else:
                        st.error(result.get("msg", "删除失败"))
        else:
            st.info("暂无类目数据")
    else:
        st.error(result.get("msg", "获取失败"))


# Tab 2: Category Tree
with tab2:
    st.subheader("类目树结构")

    if st.button("🔄 刷新树"):
        st.rerun()

    result = api.get_category_tree(env=env)

    if result.get("code") == 200:
        tree_data = result.get("data", [])

        def display_tree(nodes, indent=0):
            for node in nodes:
                st.write("  " * indent + f"📁 {node['name']} (ID: {node['id']}, Level: {node['level']})")
                if node.get("children"):
                    display_tree(node["children"], indent + 1)

        if tree_data:
            display_tree(tree_data)
        else:
            st.info("暂无类目数据")
    else:
        st.error(result.get("msg", "获取失败"))


# Tab 3: Create Category
with tab3:
    st.subheader("创建新类目")

    with st.form("create_category_form"):
        name = st.text_input("类目名称", max_chars=64)
        level = st.selectbox("层级", [1, 2], format_func=lambda x: f"Level {x}" if x == 1 else f"Level {x} (二级)")

        parent_id = None
        if level == 2:
            # Get parent categories
            parent_result = api.get_categories(env=env)
            if parent_result.get("code") == 200:
                categories = parent_result.get("data", {}).get("items", [])
                level1_cats = [c for c in categories if c.get("level") == 1]
                if level1_cats:
                    parent_options = {c["id"]: c["name"] for c in level1_cats}
                    parent_id = st.selectbox("父类目", options=list(parent_options.keys()), format_func=lambda x: parent_options[x])
                else:
                    st.warning("请先创建一级类目")
            else:
                st.error("获取类目失败")

        creator = st.text_input("创建人", value="admin")

        submitted = st.form_submit_button("创建", type="primary")

        if submitted:
            if not name:
                st.error("请输入类目名称")
            else:
                data = {
                    "env": env,
                    "name": name,
                    "level": level,
                    "creator": creator
                }
                if parent_id:
                    data["parent_id"] = parent_id

                result = api.create_category(data)
                if result.get("code") == 201:
                    st.success("创建成功!")
                    st.rerun()
                else:
                    st.error(result.get("msg", "创建失败"))
