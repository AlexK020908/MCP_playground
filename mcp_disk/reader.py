"""
Read text and PDF files from a folder; return concatenated content. Used by academics MCP.
"""
from __future__ import annotations

from pathlib import Path

TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}
MAX_FILE_CHARS = 30_000
MAX_TOTAL_CHARS = 200_000
MAX_PDF_PAGES = 500


def _get_pypdf():
    try:
        import pypdf
        return pypdf
    except ImportError:
        try:
            import PyPDF2 as pypdf
            return pypdf
        except ImportError:
            return None


def read_folder_contents(
    folder: Path,
    *,
    max_chars: int = MAX_TOTAL_CHARS,
    text_extensions: frozenset[str] | None = None,
    max_file_chars: int = MAX_FILE_CHARS,
    max_pdf_pages: int = MAX_PDF_PAGES,
) -> str:
    """
    Read all .txt/.md and PDF files under folder; return a single string.
    PDF text is extracted if pypdf (or PyPDF2) is installed.
    """
    text_ext = text_extensions or frozenset(TEXT_EXTENSIONS)
    lines = [f"Folder: {folder}", ""]
    pypdf = _get_pypdf()

    for f in sorted(folder.rglob("*")):
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext in text_ext:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                lines.append(f"--- {f.name} ---")
                lines.append(content[:max_file_chars])
                lines.append("")
            except Exception as e:
                lines.append(f"--- {f.name} (error: {e}) ---")
                lines.append("")
        elif ext == ".pdf" and pypdf:
            try:
                reader = pypdf.PdfReader(str(f))
                parts = []
                for page in reader.pages[:max_pdf_pages]:
                    parts.append(page.extract_text() or "")
                content = "\n".join(parts)[:max_file_chars]
                lines.append(f"--- {f.name} (PDF) ---")
                lines.append(content)
                lines.append("")
            except Exception as e:
                lines.append(f"--- {f.name} (PDF error: {e}) ---")
                lines.append("")
        elif ext == ".pdf":
            lines.append(f"--- {f.name} --- (install pypdf to extract text)")
            lines.append("")

    result = "\n".join(lines)
    if len(result) > max_chars:
        result = result[:max_chars] + "\n\n... (truncated)"
    return result
