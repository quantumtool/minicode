"""Runtime configuration loaded from environment variables and an optional .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    provider: str
    model: str
    api_mode: str
    api_key: str
    base_url: str | None
    max_turns: int
    max_output_tokens: int
    command_timeout: int

    @classmethod
    def from_env(
        cls,
        *,
        provider: str | None = None,
        model: str | None = None,
        api_mode: str | None = None,
        max_turns: int | None = None,
    ) -> "Settings":
        configured_env_file = os.getenv("MINICODE_ENV_FILE")
        if configured_env_file:
            load_dotenv(dotenv_path=Path(configured_env_file).expanduser(), override=False)
        else:
            candidates = (
                Path.cwd() / ".env",
                Path.home() / ".minicode" / ".env",
                Path(__file__).resolve().parents[1] / ".env",
            )
            for candidate in candidates:
                if candidate.is_file():
                    load_dotenv(dotenv_path=candidate, override=False)

        selected_provider = (provider or os.getenv("MINICODE_PROVIDER", "openai")).strip().lower()
        if selected_provider not in {"openai", "anthropic"}:
            raise ValueError("MINICODE_PROVIDER must be 'openai' or 'anthropic'.")

        configured_base_url = (
            os.getenv("OPENAI_BASE_URL")
            if selected_provider == "openai"
            else os.getenv("ANTHROPIC_BASE_URL")
        )
        base_url = configured_base_url.strip() if configured_base_url and configured_base_url.strip() else None
        if selected_provider == "openai":
            selected_api_mode = (api_mode or os.getenv("MINICODE_OPENAI_API", "auto")).strip().lower()
            if selected_api_mode == "auto":
                selected_api_mode = "chat_completions" if base_url else "responses"
            if selected_api_mode not in {"responses", "chat_completions"}:
                raise ValueError("MINICODE_OPENAI_API must be 'responses' or 'chat_completions'.")
        else:
            selected_api_mode = "responses"

        key_name = "OPENAI_API_KEY" if selected_provider == "openai" else "ANTHROPIC_API_KEY"
        api_key = os.getenv(key_name, "").strip()
        selected_model = (model or os.getenv("MINICODE_MODEL") or os.getenv("MODEL_NAME", "")).strip()
        configured_max_turns = max_turns if max_turns is not None else int(os.getenv("MINICODE_MAX_TURNS", "24"))
        max_output_tokens = int(os.getenv("MINICODE_MAX_OUTPUT_TOKENS", "8192"))
        command_timeout = int(os.getenv("MINICODE_COMMAND_TIMEOUT", "45"))
        if configured_max_turns < 1:
            raise ValueError("MINICODE_MAX_TURNS must be greater than zero.")
        if max_output_tokens < 1:
            raise ValueError("MINICODE_MAX_OUTPUT_TOKENS must be greater than zero.")

        return cls(
            provider=selected_provider,
            model=selected_model,
            api_mode=selected_api_mode,
            api_key=api_key,
            base_url=base_url,
            max_turns=configured_max_turns,
            max_output_tokens=max_output_tokens,
            command_timeout=min(max(command_timeout, 1), 120),
        )
