"""Command-line interface for MiniCode."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table
from rich.text import Text

from minicode.config import Settings
from minicode.providers import create_provider
from minicode.sessions import SessionStore
from minicode.team import MiniCodeTeam

app = typer.Typer(
    name="minicode",
    help="A local multi-agent coding assistant with explicit workspace approvals.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _settings(
    *,
    provider: str | None = None,
    model: str | None = None,
    api_mode: str | None = None,
    max_turns: int | None = None,
) -> Settings:
    try:
        return Settings.from_env(
            provider=provider,
            model=model,
            api_mode=api_mode,
            max_turns=max_turns,
        )
    except (ValueError, TypeError) as exc:
        console.print(Text(f"Configuration error: {exc}", style="red"))
        raise typer.Exit(code=2) from exc


def _team(
    settings: Settings,
    workspace: Path,
    approve_all: bool,
) -> MiniCodeTeam:
    try:
        provider = create_provider(settings)
        return MiniCodeTeam(provider, settings, workspace, approve_all=approve_all)
    except (ValueError, ImportError) as exc:
        console.print(Text(f"Configuration error: {exc}", style="red"))
        raise typer.Exit(code=2) from exc


def _show_result(session: dict, result: str, artifact_dir: Path) -> None:
    console.print(Text("\nMiniCode 本轮已结束。", style="bold green"))
    console.print(result, markup=False)
    console.print(f"\nSession: {escape(session['id'])}")
    console.print(f"Planning artifacts: {escape(str(artifact_dir))}")


@app.command()
def run(
    idea: str = typer.Argument(..., help="Describe the change or project to implement."),
    workspace: Path = typer.Option(
        Path.cwd(), "--workspace", "-w", exists=True, file_okay=False, dir_okay=True, resolve_path=True
    ),
    provider: str | None = typer.Option(None, "--provider", help="Override MINICODE_PROVIDER."),
    model: str | None = typer.Option(None, "--model", help="Override MINICODE_MODEL."),
    openai_api: str | None = typer.Option(
        None, "--openai-api", help="OpenAI mode: responses or chat_completions."
    ),
    max_turns: int | None = typer.Option(None, "--max-turns", min=1, max=200),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Automatically approve file writes and shell commands. Use only in a disposable, isolated workspace.",
    ),
) -> None:
    """Create a plan, then implement it in the selected workspace."""
    settings = _settings(provider=provider, model=model, api_mode=openai_api, max_turns=max_turns)
    team = _team(settings, workspace, yes)
    try:
        session, result, artifact_dir = team.run(idea)
    except Exception as exc:
        message = str(exc).replace(settings.api_key, "[redacted]") if settings.api_key else str(exc)
        console.print(Text(f"MiniCode stopped: {message}", style="red"))
        raise typer.Exit(code=1) from exc
    _show_result(session, result, artifact_dir)


@app.command()
def plan(
    idea: str = typer.Argument(..., help="Describe the project to plan."),
    workspace: Path = typer.Option(
        Path.cwd(), "--workspace", "-w", exists=True, file_okay=False, dir_okay=True, resolve_path=True
    ),
    provider: str | None = typer.Option(None, "--provider"),
    model: str | None = typer.Option(None, "--model"),
    openai_api: str | None = typer.Option(None, "--openai-api"),
) -> None:
    """Generate and save the PM and Architect documents without editing the workspace."""
    settings = _settings(provider=provider, model=model, api_mode=openai_api)
    team = _team(settings, workspace, False)
    try:
        session, artifact_dir = team.plan(idea)
    except Exception as exc:
        message = str(exc).replace(settings.api_key, "[redacted]") if settings.api_key else str(exc)
        console.print(Text(f"MiniCode stopped: {message}", style="red"))
        raise typer.Exit(code=1) from exc
    console.print(f"Plan saved for session [cyan]{session['id']}[/cyan]: {artifact_dir}")


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="ID printed by a previous run."),
    message: str = typer.Argument(..., help="What MiniCode should do next."),
    workspace: Path | None = typer.Option(None, "--workspace", "-w", exists=True, file_okay=False),
    max_turns: int | None = typer.Option(None, "--max-turns", min=1, max=200),
    yes: bool = typer.Option(False, "--yes", help="Automatically approve writes and commands in this workspace."),
) -> None:
    """Continue a saved Developer Agent session."""
    store = SessionStore()
    try:
        saved = store.load(session_id)
    except ValueError as exc:
        console.print(Text(str(exc), style="red"))
        raise typer.Exit(code=2) from exc
    selected_workspace = (workspace or Path(saved["workspace"])).resolve()
    settings = _settings(
        provider=saved["provider"],
        model=saved["model"],
        api_mode=saved["api_mode"],
        max_turns=max_turns,
    )
    team = _team(settings, selected_workspace, yes)
    try:
        session, result, artifact_dir = team.resume(session_id, message)
    except Exception as exc:
        message_text = str(exc).replace(settings.api_key, "[redacted]") if settings.api_key else str(exc)
        console.print(Text(f"MiniCode stopped: {message_text}", style="red"))
        raise typer.Exit(code=1) from exc
    _show_result(session, result, artifact_dir)


@app.command("sessions")
def list_sessions() -> None:
    """List local sessions without printing their conversation contents."""
    rows = SessionStore().list()
    if not rows:
        console.print("No saved sessions.")
        return
    table = Table("ID", "Updated", "Workspace", "Task")
    for row in rows:
        table.add_row(*(escape(row[key]) for key in ("id", "updated_at", "workspace")), escape(row["idea"][:80]))
    console.print(table)


@app.command()
def forget(
    session_id: str = typer.Argument(..., help="ID of the local session to remove."),
    yes: bool = typer.Option(False, "--yes", help="Remove without a confirmation prompt."),
) -> None:
    """Delete a saved conversation and its local planning artifacts."""
    store = SessionStore()
    try:
        store.load(session_id)
    except ValueError as exc:
        console.print(Text(str(exc), style="red"))
        raise typer.Exit(code=2) from exc
    if not yes and not typer.confirm(f"Delete session {session_id} and its local artifacts?", default=False):
        console.print("Cancelled.")
        raise typer.Exit()
    store.delete(session_id)
    console.print(f"Deleted session {session_id}.")


@app.command()
def version() -> None:
    """Show the installed MiniCode version."""
    from minicode import __version__

    console.print(__version__)
