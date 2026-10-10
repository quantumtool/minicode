"""Anthropic Messages API adapter with native tool-use round trips."""

from __future__ import annotations

from typing import Any

from anthropic import Anthropic

from minicode.config import Settings
from minicode.models import AgentTurn, ToolCall


def _plain(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    return dict(value)


class AnthropicMessagesProvider:
    def __init__(self, settings: Settings) -> None:
        client_options: dict[str, Any] = {"api_key": settings.api_key}
        if settings.base_url:
            client_options["base_url"] = settings.base_url
        self.client = Anthropic(**client_options)
        self.settings = settings

    def complete(
        self,
        system: str,
        history: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
    ) -> AgentTurn:
        options: dict[str, Any] = {
            "model": self.settings.model,
            "system": system,
            "messages": history,
            "max_tokens": self.settings.max_output_tokens,
        }
        if tool_schemas:
            options["tools"] = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["parameters"],
                }
                for tool in tool_schemas
            ]
        response = self.client.messages.create(**options)

        blocks = [_plain(block) for block in response.content]
        calls = [
            ToolCall(
                call_id=block.get("id", ""),
                name=block.get("name", ""),
                arguments=block.get("input") if isinstance(block.get("input"), dict) else {},
            )
            for block in blocks
            if block.get("type") == "tool_use"
        ]
        text = "\n".join(block.get("text", "") for block in blocks if block.get("type") == "text")
        return AgentTurn(
            text=text,
            assistant_items=[{"role": "assistant", "content": blocks}],
            tool_calls=calls,
        )

    def tool_result_items(self, results: list[tuple[str, str]]) -> list[dict[str, Any]]:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": call_id, "content": output}
                    for call_id, output in results
                ],
            }
        ]

    def user_message(self, content: str) -> dict[str, Any]:
        return {"role": "user", "content": content}

    def append_user_message(self, history: list[dict[str, Any]], content: str) -> None:
        if history and history[-1].get("role") == "user":
            previous = history[-1].get("content", "")
            if isinstance(previous, str):
                history[-1]["content"] = [
                    {"type": "text", "text": previous},
                    {"type": "text", "text": content},
                ]
            elif isinstance(previous, list):
                previous.append({"type": "text", "text": content})
            else:
                history.append(self.user_message(content))
            return
        history.append(self.user_message(content))
