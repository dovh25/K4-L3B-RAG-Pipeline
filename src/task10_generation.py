"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation. Nếu thiếu evidence, hãy từ chối xác minh."""


from .contracts import validate_generation_result


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context để giảm lost-in-the-middle."""
    if len(chunks) <= 2:
        return [dict(chunk) for chunk in chunks]
    # Phân bố xen kẽ: chẵn ở đầu theo thứ tự tăng, lẻ ở cuối theo thứ tự giảm
    front = [dict(chunk) for chunk in chunks[::2]]
    back = [dict(chunk) for chunk in chunks[1::2]]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label cho từng document."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", f"Doc {index}")
        source = metadata.get("source", "Unknown")
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi LLM (Gemini / OpenAI / Anthropic) theo cấu hình .env."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()
    model = os.getenv("LLM_MODEL", LLM_MODEL)

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY chưa được thiết lập trong .env")

        from google import genai
        client = genai.Client(api_key=api_key)
        prompt_content = f"{system_prompt}\n\n{user_message}"

        # Danh sách model ưu tiên (tránh các model bị 503 high demand)
        candidate_models = [
            model,
            "gemini-3.1-flash-lite",
            "gemini-flash-latest",
            "gemini-3.8-flash",
            "gemini-3.5-flash",
        ]
        # Lọc bỏ rỗng và trùng lặp
        ordered_models = []
        for m in candidate_models:
            if m and m not in ordered_models:
                ordered_models.append(m)

        last_error = None
        for m in ordered_models:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt_content,
                )
                if response and response.text:
                    return response.text
            except Exception as exc:
                last_error = exc
                continue

        raise RuntimeError(f"Lỗi khi gọi Gemini API với các models: {last_error}")

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY chưa được thiết lập trong .env")
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content or ""

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY chưa được thiết lập trong .env")
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model or "claude-3-5-haiku-latest",
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1024,
            temperature=TEMPERATURE,
        )
        return message.content[0].text

    raise ValueError(f"Không hỗ trợ LLM_PROVIDER: {provider}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult kèm trích dẫn nguồn hoặc safe refusal."""
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        result = {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }
        validate_generation_result(result)
        return result

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = (
        f"Dưới đây là các tài liệu tham khảo:\n\n{context}\n\n"
        f"Câu hỏi: {query}\n\n"
        f"Hãy trả lời câu hỏi dựa trên các tài liệu trên và trích dẫn rõ tên tài liệu/nguồn tương ứng."
    )

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception as exc:
        print(f"LLM call failed: {exc}")
        answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có do sự cố kết nối tới mô hình."

    retrieval_source = chunks[0]["retrieval_method"] if chunks else "none"
    result = {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }
    validate_generation_result(result)
    return result


if __name__ == "__main__":
    res = generate_with_citation("Thủ tục đăng ký hộ kinh doanh cá thể gồm những gì?")
    print("Answer:", res["answer"])
    print("Sources count:", len(res["sources"]))
    print("Retrieval source:", res["retrieval_source"])

