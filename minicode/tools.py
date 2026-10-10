"""Workspace tools exposed to the Developer Agent."""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from rich.console import Console
from rich.markup import escape
from rich.prompt import Confirm
from rich.text import Text

console = Console()
MAX_FILE_CHARS = 30_000
MAX_TOOL_OUTPUT = 24_000
SKIP_DIRS = {".git", ".minicode", ".venv", "venv", "node_modules", "__pycache__"}
PROTECTED_DIRS = {".git", ".codex", ".claude", ".minicode", ".ssh", ".aws", ".gnupg"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
SECRET_FILENAMES = {"id_rsa", "id_ed25519", "id_ecdsa", "id_dsa", ".netrc", ".npmrc", ".pypirc"}
SECRET_ENV_NAME = re.compile(
    r"(?i)(api[_-]?key|access[_-]?key|secret|token|password|credential|private[_-]?key|auth|cookie)"
)

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "list_files",
        "description": "List files and folders under a project-relative directory. Use '.' for the workspace root.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Read a text file in the workspace. Secret files such as .env and private keys are blocked.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "search_files",
        "description": "Find a literal text string in matching workspace files. pattern is a glob such as '**/*.py' or '*'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "pattern": {"type": "string"},
            },
            "required": ["query", "pattern"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Create or replace a text file inside the workspace. Requires user approval unless --yes was explicitly supplied.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "edit_file",
        "description": "Replace one exact text occurrence in a workspace file. Requires user approval unless --yes was explicitly supplied.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_command",
        "description": "Run a shell command in the workspace. Each command requires user approval unless --yes was explicitly supplied. This is not an OS sandbox.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout_seconds": {"type": "integer"},
            },
            "required": ["command", "timeout_seconds"],
            "additionalProperties": False,
        },
    },
]


def _truncate(text: str, limit: int = MAX_TOOL_OUTPUT) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n[output truncated at {limit} characters]"


class WorkspaceTools:
    def __init__(
        self,
        workspace: Path,
        *,
        approve_all: bool = False,
        command_timeout: int = 45,
    ) -> None:
        self.workspace = workspace.resolve()
        self.approve_all = approve_all
        self.command_timeout = min(max(command_timeout, 1), 120)

    def _path(self, raw_path: str, *, for_write: bool = False) -> Path:
        candidate = Path(raw_path)
        if candidate.is_absolute():
            resolved = candidate.resolve(strict=False)
        else:
            resolved = (self.workspace / candidate).resolve(strict=False)
        try:
            relative = resolved.relative_to(self.workspace)
        except ValueError as exc:
            raise ValueError("Path must stay inside the selected workspace.") from exc

        if any(part in PROTECTED_DIRS for part in relative.parts):
            raise ValueError("Access to protected runtime or tool configuration directories is blocked.")
        if for_write and any(part in {".git", ".codex", ".claude", ".minicode"} for part in relative.parts):
            raise ValueError("Writing to protected runtime directories is blocked.")
        name = resolved.name.lower()
        if name in SECRET_FILENAMES:
            raise ValueError("Access to a common credential file is blocked.")
        if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
            raise ValueError("Access to local environment files is blocked. Use .env.example for templates.")
        if resolved.suffix.lower() in SECRET_SUFFIXES:
            raise ValueError("Access to private-key files is blocked.")
        return resolved

    def _approved(self, action: str) -> bool:
        if self.approve_all:
            return True
        if not sys.stdin.isatty():
            return False
        return Confirm.ask(escape(f"Allow {action}?"), default=False)

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        handlers: dict[str, Callable[[dict[str, Any]], str]] = {
            "list_files": self._list_files,
            "read_file": self._read_file,
            "search_files": self._search_files,
            "write_file": self._write_file,
            "edit_file": self._edit_file,
            "run_command": self._run_command,
        }
        handler = handlers.get(name)
        if handler is None:
            return f"Tool error: unknown tool '{name}'."
        try:
            return _truncate(handler(arguments))
        except Exception as exc:  # Return a bounded error to the model; do not crash the session.
            return f"Tool error ({type(exc).__name__}): {exc}"

    def _list_files(self, args: dict[str, Any]) -> str:
        path = self._path(str(args.get("path", ".")))
        if not path.is_dir():
            return f"Not a directory: {path.relative_to(self.workspace)}"
        entries: list[str] = []
        for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
            if child.name in SKIP_DIRS or child.name.startswith(".DS_Store"):
                continue
            marker = "/" if child.is_dir() else ""
            entries.append(f"{child.relative_to(self.workspace).as_posix()}{marker}")
            if len(entries) >= 200:
                entries.append("[listing truncated]")
                break
        return "\n".join(entries) if entries else "(empty directory)"

    def _read_file(self, args: dict[str, Any]) -> str:
        path = self._path(str(args.get("path", "")))
        if not path.is_file():
            return "File does not exist."
        if path.stat().st_size > 1_000_000:
            return "File is larger than the 1 MB read limit."
        content = path.read_text(encoding="utf-8", errors="replace")
        return _truncate(content, MAX_FILE_CHARS)

    def _search_files(self, args: dict[str, Any]) -> str:
        query = str(args.get("query", ""))
        pattern = str(args.get("pattern", "*"))
        if not query:
            return "Search query cannot be empty."
        if ".." in Path(pattern).parts:
            return "Search pattern cannot traverse outside the workspace."
        results: list[str] = []
        folded_query = query.casefold()
        for path in self.workspace.rglob("*"):
            relative = path.relative_to(self.workspace)
            if any(part in SKIP_DIRS or part.startswith(".DS_Store") for part in relative.parts):
                continue
            pattern_match = fnmatch.fnmatchcase(relative.as_posix(), pattern)
            if pattern.startswith("**/"):
                pattern_match = pattern_match or fnmatch.fnmatchcase(relative.as_posix(), pattern[3:])
            if not path.is_file() or not pattern_match:
                continue
            try:
                path = self._path(relative.as_posix())
                if path.stat().st_size > 1_000_000:
                    continue
                lines = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError, ValueError):
                continue
            for number, line in enumerate(lines, start=1):
                if folded_query in line.casefold():
                    results.append(f"{relative.as_posix()}:{number}: {line[:500]}")
                    if len(results) >= 100:
                        results.append("[search results truncated]")
                        return "\n".join(results)
        return "\n".join(results) if results else "No matches found."

    def _write_file(self, args: dict[str, Any]) -> str:
        path = self._path(str(args.get("path", "")), for_write=True)
        relative = path.relative_to(self.workspace).as_posix()
        operation = "overwrite" if path.exists() else "create"
        content = str(args.get("content", ""))
        preview = content[:1_200]
        console.print(Text(f"Proposed {operation}: {relative} ({len(content)} characters)", style="dim"))
        if preview:
            console.print(Text(f"{preview}{'…' if len(content) > len(preview) else ''}", style="dim"))
        if not self._approved(f"{operation} {relative}"):
            return f"Denied: approval was not granted for writing {relative}."
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path(relative, for_write=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {relative} ({len(content)} characters)."

    def _edit_file(self, args: dict[str, Any]) -> str:
        path = self._path(str(args.get("path", "")), for_write=True)
        if not path.is_file():
            return "File does not exist."
        old_text = str(args.get("old_text", ""))
        new_text = str(args.get("new_text", ""))
        if not old_text:
            return "old_text cannot be empty."
        content = path.read_text(encoding="utf-8")
        count = content.count(old_text)
        if count != 1:
            return f"Expected old_text to match once; found {count} occurrences."
        relative = path.relative_to(self.workspace).as_posix()
        console.print(Text(f"Proposed edit to {relative}:", style="dim"))
        console.print(Text(f"- {old_text[:500]}\n+ {new_text[:500]}", style="dim"))
        if not self._approved(f"edit {relative}"):
            return f"Denied: approval was not granted for editing {relative}."
        path.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Updated {relative}."

    def _run_command(self, args: dict[str, Any]) -> str:
        command = str(args.get("command", "")).strip()
        if not command:
            return "Command cannot be empty."
        try:
            timeout = int(args.get("timeout_seconds", self.command_timeout))
        except (TypeError, ValueError):
            timeout = self.command_timeout
        timeout = min(max(timeout, 1), self.command_timeout, 120)
        if not self._approved(f"run command in {self.workspace}: {command}"):
            return "Denied: approval was not granted for this command."
        child_env = {
            name: value
            for name, value in os.environ.items()
            if not SECRET_ENV_NAME.search(name)
        }
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                errors="replace",
                env=child_env,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return _truncate(f"Command timed out after {timeout}s.\n{stdout}\n{stderr}")
        return _truncate(
            f"exit code: {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
