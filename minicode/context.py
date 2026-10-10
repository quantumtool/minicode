"""Load repository instructions and reusable local skills for a coding session."""

from __future__ import annotations

from pathlib import Path

MAX_CONTEXT_FILE_CHARS = 25_000
MAX_TOTAL_CONTEXT_CHARS = 80_000


def build_project_context(workspace: Path) -> str:
    sections: list[str] = []
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = workspace / name
        if path.is_file() and path.resolve().is_relative_to(workspace.resolve()):
            body = path.read_text(encoding="utf-8", errors="replace")[:MAX_CONTEXT_FILE_CHARS]
            sections.append(f"### {name}\n{body}")

    skills_root = workspace / ".minicode" / "skills"
    if skills_root.is_dir():
        for path in sorted(skills_root.glob("*/SKILL.md")):
            if not path.is_file() or not path.resolve().is_relative_to(workspace.resolve()):
                continue
            body = path.read_text(encoding="utf-8", errors="replace")[:MAX_CONTEXT_FILE_CHARS]
            sections.append(f"### Skill: {path.parent.name}\n{body}")

    return "\n\n".join(sections)[:MAX_TOTAL_CONTEXT_CHARS]
