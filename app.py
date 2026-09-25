import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="Trợ lý Pháp luật Hộ Kinh Doanh",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling for rich appearance
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .source-box {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 0.75rem 1rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 0.25rem;
    }
    .badge-method {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #E0E7FF;
        color: #3730A3;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("⚖️ Quản lý Pipeline")
    st.caption("Chủ đề: **Pháp luật cho Hộ Kinh Doanh**")
    st.markdown("---")
    top_k = st.slider("Số lượng Chunks truy xuất (top_k)", 3, 10, 5)

    st.markdown("### 📚 Tài liệu trong Hệ thống")
    st.markdown("- **Nghị định 01/2021/NĐ-CP**: Đăng ký hộ kinh doanh")
    st.markdown("- **Thông tư 40/2021/TT-BTC**: Thuế GTGT, TNCN & thuế khoán")
    st.markdown("- **Thông tư 88/2021/TT-BTC**: Chế độ kế toán & 7 mẫu sổ")
    st.markdown("- **5 Bài viết hướng dẫn thực tế**: Hóa đơn máy tính tiền, bán hàng online...")

    st.markdown("---")
    st.markdown("### 💡 Câu hỏi gợi ý:")
    sample_questions = [
        "Thủ tục đăng ký hộ kinh doanh cá thể gồm những giấy tờ gì?",
        "Hộ kinh doanh doanh thu dưới 100 triệu có phải nộp thuế không?",
        "Tỷ lệ thuế khoán đối với hộ bán buôn, bán lẻ là bao nhiêu?",
        "Hộ kinh doanh nộp thuế kê khai phải mở những sổ kế toán nào?",
        "Hộ kinh doanh có được mở nhiều địa điểm kinh doanh không?",
    ]
    for q in sample_questions:
        if st.button(q, key=f"q_{q[:15]}", use_container_width=True):
            st.session_state.preset_query = q

    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Header
st.markdown('<div class="main-header">⚖️ Trợ lý Pháp luật Hộ Kinh Doanh</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Hệ thống hỏi đáp pháp luật hỗ trợ tra cứu quy định thành lập, thuế, hóa đơn và kế toán cho hộ kinh doanh (RAG Hybrid Search + Citation).</div>',
    unsafe_allow_html=True,
)

# Hiển thị lịch sử tin nhắn
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            retrieval_src = message.get("retrieval_source", "hybrid")
            st.markdown(f'<span class="badge-method">🔍 Nguồn truy xuất: {retrieval_src.upper()}</span>', unsafe_allow_html=True)
            with st.expander(f"📖 Xem chi tiết {len(message['sources'])} nguồn tài liệu trích dẫn"):
                for idx, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    st.markdown(
                        f"""
                        **[{idx}] {meta.get('title', 'Tài liệu')}**  
                        - *Tập tin nguồn:* `{meta.get('source', '')}` | *Điểm tương đồng:* `{src.get('score', 0):.4f}` | *Phương thức:* `{src.get('retrieval_method', '')}`  
                        > {src.get('content', '')}
                        ---
                        """
                    )

# Input
preset = st.session_state.pop("preset_query", None)
query = st.chat_input("Nhập câu hỏi về pháp luật hộ kinh doanh...")
final_query = preset or query

if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})

    with st.chat_message("user"):
        st.markdown(final_query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và tổng hợp câu trả lời..."):
            gen_result = generate_with_citation(final_query, top_k=top_k)
            answer = gen_result["answer"]
            sources = gen_result["sources"]
            retrieval_source = gen_result["retrieval_source"]

            st.markdown(answer)

            if sources:
                st.markdown(f'<span class="badge-method">🔍 Nguồn truy xuất: {retrieval_source.upper()}</span>', unsafe_allow_html=True)
                with st.expander(f"📖 Xem chi tiết {len(sources)} nguồn tài liệu trích dẫn"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        st.markdown(
                            f"""
                            **[{idx}] {meta.get('title', 'Tài liệu')}**  
                            - *Tập tin nguồn:* `{meta.get('source', '')}` | *Điểm tương đồng:* `{src.get('score', 0):.4f}` | *Phương thức:* `{src.get('retrieval_method', '')}`  
                            > {src.get('content', '')}
                            ---
                            """
                        )

    # Lưu vào session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })

