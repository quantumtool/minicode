"""OpenAI Responses API and OpenAI-compatible Chat Completions adapters."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from minicode.config import Settings
from minicode.models import AgentTurn, ToolCall


def _plain(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    return dict(value)


class OpenAIProvider:
    def __init__(self, settings: Settings) -> None:
        client_options: dict[str, Any] = {"api_key": settings.api_key}
        if settings.base_url:
            client_options["base_url"] = settings.base_url
        self.client = OpenAI(**client_options)
        self.settings = settings

    def complete(
        self,
        system: str,
        history: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
    ) -> AgentTurn:
        if self.settings.api_mode == "chat_completions":
            return self._chat_completions(system, history, tool_schemas)
        return self._responses(system, history, tool_schemas)

    def _responses(
        self,
        system: str,
        history: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
    ) -> AgentTurn:
        options: dict[str, Any] = {
            "model": self.settings.model,
            "instructions": system,
            "input": history,
            "store": False,
            "max_output_tokens": self.settings.max_output_tokens,
        }
        if tool_schemas:
            options["tools"] = [{**tool, "strict": True} for tool in tool_schemas]
        response = self.client.responses.create(**options)

        items = [_plain(item) for item in response.output]
        calls: list[ToolCall] = []
        for item in items:
            if item.get("type") != "function_call":
                continue
            try:
                arguments = json.loads(item.get("arguments") or "{}")
            except json.JSONDecodeError:
                arguments = {}
            calls.append(
                ToolCall(
                    call_id=item.get("call_id", item.get("id", "")),
                    name=item.get("name", ""),
                    arguments=arguments if isinstance(arguments, dict) else {},
                )
            )
        return AgentTurn(text=response.output_text or "", assistant_items=items, tool_calls=calls)

    def _chat_completions(
        self,
        system: str,
        history: list[dict[str, Any]],
        tool_schemas: list[dict[str, Any]],
    ) -> AgentTurn:
        messages = [{"role": "system", "content": system}, *history]
        options: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages,
            "max_tokens": self.settings.max_output_tokens,
        }
        if tool_schemas:
            options["tools"] = [
                {"type": "function", "function": {k: v for k, v in tool.items() if k != "type"}}
                for tool in tool_schemas
            ]
        response = self.client.chat.completions.create(**options)
        message = response.choices[0].message
        item = _plain(message)
        calls: list[ToolCall] = []
        for call in item.get("tool_calls") or []:
            function = call.get("function") or {}
            try:
                arguments = json.loads(function.get("arguments") or "{}")
            except json.JSONDecodeError:
                arguments = {}
            calls.append(
                ToolCall(
                    call_id=call.get("id", ""),
                    name=function.get("name", ""),
                    arguments=arguments if isinstance(arguments, dict) else {},
                )
            )
        return AgentTurn(text=item.get("content") or "", assistant_items=[item], tool_calls=calls)

    def tool_result_items(self, results: list[tuple[str, str]]) -> list[dict[str, Any]]:
        if self.settings.api_mode == "chat_completions":
            return [
                {"role": "tool", "tool_call_id": call_id, "content": output}
                for call_id, output in results
            ]
        return [
            {"type": "function_call_output", "call_id": call_id, "output": output}
            for call_id, output in results
        ]

    def user_message(self, content: str) -> dict[str, Any]:
        return {"role": "user", "content": content}

    def append_user_message(self, history: list[dict[str, Any]], content: str) -> None:
        history.append(self.user_message(content))
