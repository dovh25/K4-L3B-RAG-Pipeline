"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Fuse hai danh sách bằng RRF đúng một lần.
    3. Lấy best cosine score gốc từ dense results.
    4. Nếu score dưới threshold, thử PageIndex fallback.
    5. Nếu fallback lỗi, trả hybrid results thay vì crash.

Không so sánh threshold với RRF score vì hai thang đo khác nhau.
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


import os
import dotenv

dotenv.load_dotenv()

try:
    SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.35") or "0.35")
except ValueError:
    SCORE_THRESHOLD = 0.35

DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult tuân thủ contract."""
    if top_k <= 0 or not query.strip():
        return []

    fetch_k = max(top_k * 2, 10)
    dense = semantic_search(query, top_k=fetch_k)
    sparse = lexical_search(query, top_k=fetch_k)

    best_dense_score = float(dense[0]["score"]) if dense else 0.0

    # Nếu score dense gốc dưới threshold, thử kích hoạt vectorless fallback (PageIndex)
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback[:top_k]
        except Exception as exc:
            print(f"Fallback provider error: {exc}. Using hybrid instead.")

    # Fuse bằng RRF đúng một lần
    if use_reranking:
        hybrid = rerank_rrf([dense, sparse], top_k=top_k)
        return hybrid[:top_k]
    else:
        return dense[:top_k]


if __name__ == "__main__":
    for res in retrieve("đăng ký hộ kinh doanh", top_k=3):
        print(f"[{res['retrieval_method']}] {res['score']:.4f}: {res['metadata']['title']}")

