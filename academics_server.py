"""
Disk / academics MCP server: list and read course/quiz materials from local folders.
Uses mcp_disk for config, paths, and reading. Configure ACADEMICS_BASE in .env (default E:/).
"""
from __future__ import annotations

from fastmcp import FastMCP

from mcp_disk import get_academics_base, get_course_dir, get_quiz_folder, read_folder_contents

mcp = FastMCP("Disk / Academics (course & quiz materials)")


@mcp.tool()
def school_resources(
    school_name: str,
    course_name: str,
    resource_type: str = "all",
) -> str:
    """
    List contents of a course folder under the academics base.
    school_name: e.g. 'ubc'. course_name: e.g. 'cpsc440'.
    resource_type: 'all' (course root), 'lectures', or 'homework'.
    Returns the folder path and list of entry names.
    """
    work_dir = get_course_dir(school_name, course_name)
    if resource_type == "all":
        if not work_dir.exists():
            return f"No course directory found: {work_dir}"
        items = [p.name for p in sorted(work_dir.iterdir())]
        return f"{work_dir}\n" + "\n".join(items)
    if resource_type == "lectures":
        target = work_dir / "lectures"
        if not target.exists():
            return f"Not found: {target}"
        items = [p.name for p in sorted(target.iterdir())]
        return f"{target}\n" + "\n".join(items)
    if resource_type == "homework":
        target = work_dir / "homework"
        if not target.exists():
            return f"Not found: {target}"
        items = [p.name for p in sorted(target.iterdir())]
        return f"{target}\n" + "\n".join(items)
    return f"Unknown resource_type: {resource_type}. Use 'all', 'lectures', or 'homework'."


@mcp.tool()
def get_quiz_materials(
    school_name: str,
    course_name: str,
    quiz_id: str,
) -> str:
    """
    Read all quiz materials for a course: text, markdown, and PDF under the quiz folder.
    school_name: e.g. 'ubc'. course_name: e.g. 'cpsc440'. quiz_id: e.g. '5' or 'quiz5'.
    Looks under academics/{school}/{course}/lectures/ for quiz 5, quiz/5, quiz5, etc.
    Returns concatenated file contents for study.
    """
    folder = get_quiz_folder(school_name, course_name, quiz_id)
    if folder is None:
        base = get_course_dir(school_name, course_name, subdir="lectures")
        tried = [
            base / f"quiz {quiz_id}",
            base / "quiz" / quiz_id,
            base / f"quiz{quiz_id}",
            base / f"quiz_{quiz_id}",
        ]
        listing = list(base.iterdir()) if base.exists() else []
        return (
            f"No quiz folder found. Tried: {[str(p) for p in tried]}. "
            f"Listing base: {listing}"
        )
    return read_folder_contents(folder)


if __name__ == "__main__":
    mcp.run(transport="stdio")
