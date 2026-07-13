from __future__ import annotations

import os

from langchain_core.language_models.chat_models import BaseChatModel


def build_default_llm(provider: str | None = None, model_name: str | None = None) -> BaseChatModel:
    provider = provider or os.getenv("GATEKEEPER_MODEL_PROVIDER", "openai")
    model_name = model_name or os.getenv("GATEKEEPER_MODEL", "gpt-4.1")

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model_name, temperature=0)

    raise ValueError(
        f"Unsupported GATEKEEPER_MODEL_PROVIDER={provider!r}. "
        "Add a provider adapter in gatekeeper_runtime.llm.build_default_llm()."
    )
