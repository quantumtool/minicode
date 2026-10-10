"""PM → Architect → Developer coordinator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console

from minicode.agents.architect import ArchitectAgent
from minicode.agents.developer import DeveloperAgent
from minicode.agents.pm import PMAgent
from minicode.config import Settings
from minicode.context import build_project_context
from minicode.sessions import SessionStore
from minicode.tools import WorkspaceTools

console = Console()


class MiniCodeTeam:
    def __init__(
        self,
        provider: Any,
        settings: Settings,
        workspace: Path,
        *,
        approve_all: bool = False,
        store: SessionStore | None = None,
    ) -> None:
        self.provider = provider
        self.settings = settings
        self.workspace = workspace.resolve()
        self.store = store or SessionStore()
        self.pm = PMAgent(provider)
        self.architect = ArchitectAgent(provider)
        tools = WorkspaceTools(
            self.workspace,
            approve_all=approve_all,
            command_timeout=settings.command_timeout,
        )
        self.developer = DeveloperAgent(provider, tools, settings.max_turns)

    def _new_plan(self, idea: str) -> dict[str, Any]:
        session = self.store.new(
            workspace=self.workspace,
            idea=idea,
            provider=self.settings.provider,
            model=self.settings.model,
            api_mode=self.settings.api_mode,
        )
        console.print("[yellow]PM Agent 正在整理需求...[/yellow]")
        session["prd"] = self.pm.run(idea)
        console.print("[yellow]Architect Agent 正在制定方案...[/yellow]")
        session["architecture"] = self.architect.run(session["prd"])
        self.store.save(session)
        self._save_artifacts(session)
        return session

    def _save_artifacts(self, session: dict[str, Any]) -> Path:
        run_dir = self.store.runs_root / session["id"]
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "idea.txt").write_text(session["idea"], encoding="utf-8")
        (run_dir / "prd.md").write_text(session["prd"], encoding="utf-8")
        (run_dir / "architecture.md").write_text(session["architecture"], encoding="utf-8")
        return run_dir

    def plan(self, idea: str) -> tuple[dict[str, Any], Path]:
        session = self._new_plan(idea)
        return session, self._save_artifacts(session)

    def run(self, idea: str) -> tuple[dict[str, Any], str, Path]:
        session = self._new_plan(idea)
        console.print("[yellow]Developer Agent 正在工作区中实现...[/yellow]")
        result = self._develop(session)
        return session, result, self._save_artifacts(session)

    def resume(self, session_id: str, followup: str) -> tuple[dict[str, Any], str, Path]:
        session = self.store.load(session_id)
        if Path(session["workspace"]).resolve() != self.workspace:
            raise ValueError("Resume this session from its original workspace, or pass the matching --workspace.")
        if (
            session["provider"] != self.settings.provider
            or session["model"] != self.settings.model
            or session["api_mode"] != self.settings.api_mode
        ):
            raise ValueError("The saved session uses a different provider or model configuration.")
        console.print(f"[yellow]正在继续会话 {session_id}...[/yellow]")
        result = self.developer.run(
            idea=session["idea"],
            prd=session["prd"],
            architecture=session["architecture"],
            project_context=build_project_context(self.workspace),
            history=session["developer_history"],
            save_history=lambda: self.store.save(session),
            followup=followup,
        )
        self.store.save(session)
        return session, result, self._save_artifacts(session)

    def _develop(self, session: dict[str, Any]) -> str:
        return self.developer.run(
            idea=session["idea"],
            prd=session["prd"],
            architecture=session["architecture"],
            project_context=build_project_context(self.workspace),
            history=session["developer_history"],
            save_history=lambda: self.store.save(session),
        )
