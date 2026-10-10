"""Provider-neutral model/tool loop for the Developer Agent."""

from __future__ import annotations

from typing import Any, Callable

from rich.console import Console
from rich.markup import escape

from minicode.tools import TOOL_SCHEMAS, WorkspaceTools

console = Console()


class AgentLoop:
    def __init__(self, provider: Any, tools: WorkspaceTools, max_turns: int) -> None:
        self.provider = provider
        self.tools = tools
        self.max_turns = max(1, max_turns)

    def run(
        self,
        *,
        system: str,
        history: list[dict[str, Any]],
        save_history: Callable[[], None],
    ) -> str:
        for _ in range(self.max_turns):
            turn = self.provider.complete(system, history, TOOL_SCHEMAS)
            history.extend(turn.assistant_items)
            if not turn.tool_calls:
                save_history()
                return turn.text.strip() or "The model returned no final text."

            tool_results: list[tuple[str, str]] = []
            for call in turn.tool_calls:
                console.print(f"[cyan]Tool:[/cyan] {escape(call.name)}")
                result = self.tools.execute(call.name, call.arguments)
                tool_results.append((call.call_id, result))
            history.extend(self.provider.tool_result_items(tool_results))
            save_history()

        save_history()
        return (
            f"Stopped after reaching the configured limit of {self.max_turns} model turns. "
            "Resume this session to continue."
        )
