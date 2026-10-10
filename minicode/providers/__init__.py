"""Provider adapters for the OpenAI and Anthropic APIs."""

from minicode.config import Settings
from minicode.providers.anthropic_messages import AnthropicMessagesProvider
from minicode.providers.openai_provider import OpenAIProvider


def create_provider(settings: Settings):
    if not settings.model:
        raise ValueError("Set MINICODE_MODEL to a model name supported by your provider.")
    if not settings.api_key:
        key_name = "OPENAI_API_KEY" if settings.provider == "openai" else "ANTHROPIC_API_KEY"
        raise ValueError(f"Set {key_name} in your environment or local .env file.")
    if settings.provider == "anthropic":
        return AnthropicMessagesProvider(settings)
    return OpenAIProvider(settings)
