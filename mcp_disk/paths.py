"""
Resolve course and quiz folder paths for the academics MCP.
"""
from __future__ import annotations

from pathlib import Path

from mcp_disk.config import get_academics_base


def _norm(s: str) -> str:
    return s.lower().replace(" ", "").strip()


def get_course_dir(school_name: str, course_name: str, *, subdir: str | None = None) -> Path:
    """
    Return Path to academics/{school}/{course}, optionally with a subdir (e.g. lectures).
    Does not check existence.
    """
    base = get_academics_base()
    path = base / "academics" / _norm(school_name) / _norm(course_name)
    if subdir:
        path = path / subdir.strip()
    return path


def get_quiz_folder(school_name: str, course_name: str, quiz_id: str) -> Path | None:
    """
    Return the first existing folder that looks like the requested quiz.
    Tries: lectures/quiz 5, lectures/quiz/5, lectures/quiz5, etc.
    Returns None if no candidate exists.
    """
    base = get_course_dir(school_name, course_name, subdir="lectures")
    if not base.exists():
        return None

    candidates = [
        base / f"quiz {quiz_id}",
        base / "quiz" / quiz_id,
        base / "quiz" / f"quiz{quiz_id}",
        base / f"quiz{quiz_id}",
        base / f"quiz_{quiz_id}",
        base,
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    return None
