"""Declarative agent definition — stipulate an agent without a framework.

    agent = AgentSpec(name="Private Caller", model="openai/gpt-5.4-nano").build()
    run(agent)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional, Sequence

from .protocol import CliAgent, ToolInfo

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass
class AgentSpec:
    """A backend-agnostic description of an agent the CLI can run.

    backend:
      "openrouter" — OpenAI SDK against OpenRouter (uses OPENROUTER_API_KEY)
      "openai"     — OpenAI SDK against OpenAI (uses OPENAI_API_KEY)
    """

    name: str
    model: str
    system_prompt: Optional[str] = None
    backend: str = "openrouter"
    temperature: float = 0.3
    tools: Sequence[ToolInfo] = field(default_factory=list)

    def build(self) -> CliAgent:
        from .adapters.openai_adapter import OpenAIChatAgent

        if self.backend == "openrouter":
            return OpenAIChatAgent(
                name=self.name,
                model=self.model,
                system_prompt=self.system_prompt,
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                base_url=OPENROUTER_BASE_URL,
                headers={"HTTP-Referer": "https://perpetualautomata.com", "X-Title": self.name},
                temperature=self.temperature,
                tools=self.tools,
            )
        if self.backend == "openai":
            return OpenAIChatAgent(
                name=self.name,
                model=self.model,
                system_prompt=self.system_prompt,
                temperature=self.temperature,
                tools=self.tools,
            )
        raise ValueError(f"unknown backend: {self.backend!r} (expected 'openrouter' or 'openai')")
