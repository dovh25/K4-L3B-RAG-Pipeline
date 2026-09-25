"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

import json
from pathlib import Path


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert PDF/DOCX từ data/landing/legal sang data/standardized/legal."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Thử import markitdown nếu có, nếu không thì dùng PyMuPDF (fitz)
    converter = None
    try:
        from markitdown import MarkItDown
        converter = MarkItDown()
    except ImportError:
        pass

    import fitz  # PyMuPDF fallback luôn sẵn sàng

    for path in legal_dir.iterdir():
        if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
            markdown_content = ""
            if converter:
                try:
                    result = converter.convert(str(path))
                    markdown_content = result.text_content
                except Exception:
                    pass

            # Fallback sang fitz nếu converter không khả dụng hoặc lỗi
            if not markdown_content and path.suffix.lower() == ".pdf":
                doc = fitz.open(str(path))
                pages_text = [page.get_text() for page in doc]
                doc.close()
                markdown_content = "\n\n".join(pages_text).strip()

            if markdown_content and len(markdown_content) >= 200:
                dest = output_dir / f"{path.stem}.md"
                dest.write_text(markdown_content, encoding="utf-8")
                print(f"Converted legal: {dest.name} ({len(markdown_content)} chars)")
            else:
                print(f"Warning: Empty or too short content for {path.name}")


def convert_news_articles() -> None:
    """Convert JSON từ data/landing/news sang data/standardized/news."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
        )
        full_content = header + data["content_markdown"]
        dest = output_dir / f"{path.stem}.md"
        dest.write_text(full_content, encoding="utf-8")
        print(f"Converted news: {dest.name} ({len(full_content)} chars)")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()

