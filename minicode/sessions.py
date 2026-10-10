"""Local session storage outside the project checkout."""

from __future__ import annotations

import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SessionStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or (Path.home() / ".minicode" / "sessions")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            self.root.chmod(0o700)
        except OSError:
            pass

    def new(self, *, workspace: Path, idea: str, provider: str, model: str, api_mode: str) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "id": uuid.uuid4().hex[:12],
            "created_at": now,
            "updated_at": now,
            "workspace": str(workspace.resolve()),
            "idea": idea,
            "provider": provider,
            "model": model,
            "api_mode": api_mode,
            "prd": "",
            "architecture": "",
            "developer_history": [],
        }

    def save(self, session: dict[str, Any]) -> Path:
        session["updated_at"] = datetime.now(timezone.utc).isoformat()
        destination = self.root / f"{session['id']}.json"
        temporary = destination.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            temporary.chmod(0o600)
        except OSError:
            pass
        os.replace(temporary, destination)
        return destination

    def load(self, session_id: str) -> dict[str, Any]:
        if not session_id or any(char not in "0123456789abcdef-" for char in session_id.lower()):
            raise ValueError("Invalid session ID.")
        path = self.root / f"{session_id}.json"
        if not path.is_file():
            raise ValueError(f"Session not found: {session_id}")
        try:
            session = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Session file is invalid: {session_id}") from exc
        if session.get("id") != session_id:
            raise ValueError("Session ID does not match the saved session file.")
        return session

    def list(self) -> list[dict[str, str]]:
        sessions: list[dict[str, str]] = []
        for path in self.root.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            sessions.append(
                {
                    "id": str(data.get("id", path.stem)),
                    "updated_at": str(data.get("updated_at", "")),
                    "workspace": str(data.get("workspace", "")),
                    "idea": str(data.get("idea", "")),
                }
            )
        return sorted(sessions, key=lambda item: item["updated_at"], reverse=True)

    def delete(self, session_id: str) -> None:
        self.load(session_id)
        (self.root / f"{session_id}.json").unlink()
        artifact_dir = self.runs_root / session_id
        if artifact_dir.is_dir() and not artifact_dir.is_symlink():
            shutil.rmtree(artifact_dir)

    @property
    def runs_root(self) -> Path:
        path = self.root.parent / "runs"
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            path.chmod(0o700)
        except OSError:
            pass
        return path
