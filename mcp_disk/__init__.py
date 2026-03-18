"""
Disk / academics MCP — modular helpers for reading course and quiz folders.
"""
from mcp_disk.config import get_academics_base
from mcp_disk.reader import read_folder_contents
from mcp_disk.paths import get_course_dir, get_quiz_folder

__all__ = [
    "get_academics_base",
    "read_folder_contents",
    "get_course_dir",
    "get_quiz_folder",
]
