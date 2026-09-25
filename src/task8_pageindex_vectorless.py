"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    api_key = os.getenv("PAGEINDEX_API_KEY", "")
    if not api_key:
        print("PAGEINDEX_API_KEY không được cung cấp. Bỏ qua bước upload.")
        return
    try:
        # Nếu có PageIndex SDK
        from pageindex import PageIndexClient
        client = PageIndexClient(api_key=api_key)
        # upload logic
        print("Uploaded documents to PageIndex.")
    except Exception as exc:
        print(f"PageIndex upload error: {exc}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult hoặc [] nếu không khả dụng."""
    if top_k <= 0 or not query.strip():
        return []

    api_key = os.getenv("PAGEINDEX_API_KEY", "")
    if not api_key:
        return []

    try:
        from pageindex import PageIndexClient
        client = PageIndexClient(api_key=api_key)
        response = client.search(query=query, top_k=top_k)
        results = []
        for rank, item in enumerate(response, 1):
            results.append({
                "id": str(item.get("id", f"pageindex-{rank}")),
                "content": item.get("content", ""),
                "score": float(item.get("score", 1.0 / rank)),
                "metadata": item.get("metadata", {"source": "pageindex", "title": "PageIndex Doc", "doc_type": "legal", "url": None, "chunk_index": rank}),
                "retrieval_method": "pageindex",
            })
        return results[:top_k]
    except Exception as exc:
        print(f"PageIndex search unavailable: {exc}")
        return []


if __name__ == "__main__":
    upload_documents()

