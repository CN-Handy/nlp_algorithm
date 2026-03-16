"""
FAQ System Demo - Q&A
智能问答页面
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import api_client as api

st.set_page_config(page_title="智能问答", page_icon="💬")

st.title("💬 智能问答")


# Sidebar - Settings
with st.sidebar:
    st.header("设置")

    channel = st.selectbox(
        "选择渠道",
        ["default", "wechat", "app", "web"],
        format_func=lambda x: {
            "default": "默认",
            "wechat": "微信",
            "app": "App",
            "web": "网页"
        }.get(x, x)
    )

    top_k = st.slider("返回数量", 1, 10, 3)


# Main Q&A area
st.markdown("""
## 💬 智能问答

在下方输入您的问题，系统将基于语义理解返回最匹配的FAQ答案。

支持多渠道答案：
- **默认**: 通用答案
- **微信**: 微信渠道专属答案
- **App**: App端专属答案
- **网页**: 网页端专属答案
""")

st.markdown("---")

# Question input
question = st.text_input(
    "请输入您的问题：",
    placeholder="例如：如何找回登录密码？",
    key="question_input"
)

# Ask button
if st.button("🔍 提问", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("请输入问题")
    else:
        with st.spinner("正在思考中..."):
            result = api.ask_question(question, channel=channel, top_k=top_k)

            if result.get("code") == 200:
                answers = result.get("data", {}).get("answers", [])

                if answers:
                    st.success(f"找到 {len(answers)} 个相关答案")

                    for i, answer in enumerate(answers, 1):
                        with st.container():
                            st.markdown(f"### 📌 答案 {i}")

                            # FAQ info
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{answer.get('title', 'N/A')}**")
                            with col2:
                                score = answer.get("score", 0)
                                st.metric("匹配度", f"{score:.2%}")

                            # Solution
                            solution = answer.get("solution", {})
                            if solution:
                                st.markdown("**答案内容：**")
                                st.info(solution.get("content", "N/A"))

                                # Channel info
                                st.caption(f"视角: {solution.get('perspective', 'N/A')} | 类型: {solution.get('answer_type', 'N/A')}")

                            # Highlight
                            highlight = answer.get("highlight", {})
                            if highlight:
                                st.markdown("**关键词高亮：**")
                                st.json(highlight)

                            st.markdown("---")
                else:
                    st.warning("未找到相关答案，请尝试其他问题")
            else:
                st.error(f"请求失败: {result.get('msg', 'Unknown error')}")


# Quick questions
st.markdown("### 💡 常见问题示例")

quick_questions = [
    "如何找回密码？",
    "如何修改手机号？",
    "如何查询订单？",
    "如何申请退款？",
    "如何联系客服？"
]

cols = st.columns(len(quick_questions))
for i, q in enumerate(quick_questions):
    if cols[i].button(q, key=f"quick_{i}"):
        st.session_state.question_input = q
        st.rerun()

# Show history
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if st.session_state.qa_history:
    st.markdown("---")
    st.markdown("### 📜 问答历史")

    for i, (q, a) in enumerate(reversed(st.session_state.qa_history[-5:])):
        with st.expander(f"Q: {q}"):
            if a:
                st.write(a)
