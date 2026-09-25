"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

from pathlib import Path


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"


import os
from pathlib import Path
import re
from dotenv import load_dotenv

from .contracts import validate_document


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"

_LOCAL_EMBEDDER = None


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed danh sách văn bản theo provider được cấu hình."""
    global _LOCAL_EMBEDDER
    provider = os.getenv("EMBEDDING_PROVIDER", EMBEDDING_PROVIDER).lower()

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                # Model embedding chính thức hoạt động trên API key
                response = client.models.embed_content(
                    model="models/gemini-embedding-001",
                    contents=texts,
                )
                if hasattr(response, "embeddings"):
                    return [emb.values for emb in response.embeddings]
            except Exception as exc:
                print(f"Gemini embedding note: {exc}. Trying alternative...")

    # Fallback hoặc mặc định: sentence_transformers
    if _LOCAL_EMBEDDER is None:
        from sentence_transformers import SentenceTransformer
        # Dùng all-MiniLM-L6-v2 nếu bge-m3 chưa tải để nhanh và nhẹ
        model_name = EMBEDDING_MODEL if EMBEDDING_MODEL else "all-MiniLM-L6-v2"
        try:
            _LOCAL_EMBEDDER = SentenceTransformer(model_name)
        except Exception:
            _LOCAL_EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")

    embeddings = _LOCAL_EMBEDDER.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def get_collection():
    """Mở hoặc tạo persistent Chroma collection dùng cosine distance."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown trong data/standardized/ và trả về danh sách Document."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        doc_type = "legal" if "legal" in path.parts else "news"
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        # Trích xuất URL từ header Markdown nếu có
        url = None
        url_match = re.search(r"\*\*Source:\*\*\s*(\S+)", content)
        if url_match:
            url = url_match.group(1)

        # Lấy title từ dòng đầu tiên nếu có định dạng "# Title"
        title = path.stem
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()

        doc = {
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        }
        validate_document(doc)
        documents.append(doc)
    return documents


def _recursive_split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Tự tách đoạn đệ quy phòng khi chưa có langchain_text_splitters."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(text)
    except ImportError:
        # Fallback chia theo đoạn và câu
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if len(para) > chunk_size:
                    # Cắt tiếp theo câu hoặc dấu chấm
                    sentences = para.split(". ")
                    sub_chunk = ""
                    for sent in sentences:
                        if len(sub_chunk) + len(sent) + 2 <= chunk_size:
                            sub_chunk = f"{sub_chunk}. {sent}".strip(". ")
                        else:
                            if sub_chunk:
                                chunks.append(sub_chunk)
                            sub_chunk = sent[:chunk_size]
                    if sub_chunk:
                        chunks.append(sub_chunk)
                    current_chunk = ""
                else:
                    current_chunk = para
        if current_chunk:
            chunks.append(current_chunk)
        return chunks or [text[:chunk_size]]


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id duy nhất và chunk_index."""
    chunks = []
    for document in documents:
        split_texts = _recursive_split_text(
            document["content"],
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        for index, text in enumerate(split_texts):
            clean_text = text.strip()
            if not clean_text:
                continue
            chunk = {
                "id": f"{document['id']}::chunk-{index}",
                "content": clean_text,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                },
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm vector embedding vào từng chunk."""
    if not chunks:
        return []
    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    collection = get_collection()
    # Batch upsert để tránh vượt quá giới hạn batch size
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=[chunk["metadata"] for chunk in batch],
        )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks to ChromaDB")


if __name__ == "__main__":
    run_pipeline()

