"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .contracts import validate_search_results
from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip():
        return []

    query_vector = embed_texts([query])[0]
    collection = get_collection()

    count = collection.count() if hasattr(collection, "count") else top_k
    if count == 0:
        return []

    fetch_k = min(top_k, count) if count > 0 else top_k

    response = collection.query(
        query_embeddings=[query_vector],
        n_results=fetch_k,
        include=["documents", "metadatas", "distances"],
    )

    if not response or not response["ids"] or not response["ids"][0]:
        return []

    seen_ids = set()
    results = []
    for item_id, content, metadata, distance in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)
        # Cosine distance to similarity (0 <= dist <= 2; sim = 1 - dist)
        sim_score = max(0.0, 1.0 - float(distance))
        meta = dict(metadata) if metadata else {}
        if "url" not in meta:
            meta["url"] = None
        results.append({
            "id": item_id,
            "content": content,
            "score": sim_score,
            "metadata": meta,
            "retrieval_method": "dense",
        })

    # Sort descending by score and truncate to top_k
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
    validate_search_results(sorted_results, top_k=top_k, expected_method="dense")
    return sorted_results


if __name__ == "__main__":
    for result in semantic_search("thủ tục đăng ký hộ kinh doanh", top_k=3):
        print(f"[{result['score']:.4f}] {result['metadata']['title']}: {result['content'][:80]}...")

