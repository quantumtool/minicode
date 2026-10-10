"""Shared role behavior for the PM and Architect agents."""

from __future__ import annotations

from typing import Any


class BaseAgent:
    def __init__(self, name: str, role: str, provider: Any) -> None:
        self.name = name
        self.role = role
        self.provider = provider

    def build_system(self) -> str:
        return (
            f"你是 {self.name}。你的角色是：{self.role}\n"
            "请依据输入完成分配的任务。不要声称已经执行并未执行的操作。"
        )

    def run(self, task: str) -> str:
        turn = self.provider.complete(self.build_system(), [self.provider.user_message(task)], [])
        return turn.text.strip()
