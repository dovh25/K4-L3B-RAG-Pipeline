"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""


import re
from .contracts import validate_search_results


CORPUS: list[dict] = []
_BM25_INDEX = None
_INDEXED_CORPUS_LEN = 0


def _tokenize(text: str) -> list[str]:
    """Tokenize đơn giản cho tiếng Việt và tiếng Anh."""
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = [t.strip() for t in clean.split() if t.strip()]
    return tokens


def _ensure_corpus():
    """Tự nạp corpus từ standardized nếu CORPUS rỗng."""
    global CORPUS
    if not CORPUS:
        from .task4_chunking_indexing import chunk_documents, load_documents
        docs = load_documents()
        CORPUS = chunk_documents(docs)


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ corpus chunks."""
    tokenized = [_tokenize(item["content"]) for item in corpus]
    try:
        from rank_bm25 import BM25Okapi
        return BM25Okapi(tokenized)
    except ImportError:
        # Simple BM25 fallback nếu chưa có rank_bm25
        class SimpleBM25:
            def __init__(self, docs):
                self.docs = docs

            def get_scores(self, query_tokens):
                scores = []
                q_set = set(query_tokens)
                for doc in self.docs:
                    doc_set = set(doc)
                    overlap = len(q_set & doc_set)
                    scores.append(float(overlap))
                return scores

        return SimpleBM25(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    global _BM25_INDEX, _INDEXED_CORPUS_LEN
    if top_k <= 0 or not query.strip():
        return []

    _ensure_corpus()
    if not CORPUS:
        return []

    # Rebuild index nếu corpus thay đổi (ví dụ khi mock trong test)
    if _BM25_INDEX is None or _INDEXED_CORPUS_LEN != len(CORPUS):
        _BM25_INDEX = build_bm25_index(CORPUS)
        _INDEXED_CORPUS_LEN = len(CORPUS)

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scores = _BM25_INDEX.get_scores(query_tokens)

    # Lấy các chunk có score hoặc có từ khóa khớp (phòng khi corpus nhỏ khiến IDF = 0)
    scored_items = []
    q_set = set(query_tokens)
    for idx, score in enumerate(scores):
        doc_tokens = set(_tokenize(CORPUS[idx]["content"]))
        overlap = len(q_set & doc_tokens)
        if score > 0:
            scored_items.append((idx, float(score)))
        elif overlap > 0:
            # Gán điểm dựa trên số từ trùng khi IDF của corpus nhỏ bằng 0
            scored_items.append((idx, float(overlap) * 0.1))

    # Sắp xếp giảm dần theo điểm
    scored_items.sort(key=lambda x: x[1], reverse=True)

    results = []
    seen_ids = set()
    for idx, score in scored_items[:top_k]:
        item = CORPUS[idx]
        if item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])
        meta = dict(item.get("metadata", {}))
        if "url" not in meta:
            meta["url"] = None
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": meta,
            "retrieval_method": "bm25",
        })

    validate_search_results(results, top_k=top_k, expected_method="bm25")
    return results


if __name__ == "__main__":
    for result in lexical_search("hộ kinh doanh cá thể", top_k=3):
        print(f"[{result['score']:.2f}] {result['metadata']['title']}: {result['content'][:80]}...")

