"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.

-> Dùng Jina hoặc self host hoặc bất cứ công cụ nào bạn quen
"""


from .contracts import validate_search_results


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult theo thứ hạng RRF."""
    if top_k <= 0 or not ranked_lists:
        return []

    scores = {}
    items = {}
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            item_id = item["id"]
            rrf_score = 1.0 / (k + rank)
            scores[item_id] = scores.get(item_id, 0.0) + rrf_score
            if item_id not in items:
                items[item_id] = item

    ranked_ids = sorted(scores, key=lambda i: scores[i], reverse=True)
    results = []
    for item_id in ranked_ids[:top_k]:
        item = items[item_id]
        result = {
            "id": item["id"],
            "content": item["content"],
            "score": scores[item_id],
            "metadata": item["metadata"],
            "retrieval_method": "hybrid",
        }
        results.append(result)

    validate_search_results(results, top_k=top_k, expected_method="hybrid")
    return results


if __name__ == "__main__":
    print("Task 7 RRF implemented successfully.")

