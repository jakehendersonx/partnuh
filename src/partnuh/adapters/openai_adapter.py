"""Adapter: a plain streaming chat agent over the OpenAI SDK.

Works against OpenAI or any OpenAI-compatible endpoint (e.g. OpenRouter) by
setting base_url. Tool calling is not wired yet; `tools` is display-only for now.
"""

from __future__ import annotations

import os
from typing import Dict, Iterator, List, Optional, Sequence

from ..events import Event, TextDelta
from ..protocol import ToolInfo


class OpenAIChatAgent:
    """A CliAgent backed by chat.completions streaming."""

    def __init__(
        self,
        *,
        name: str,
        model: str,
        system_prompt: Optional[str] = None,
        client=None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.3,
        headers: Optional[Dict[str, str]] = None,
        tools: Optional[Sequence[ToolInfo]] = None,
    ):
        self.name = name
        self.model = model
        self.tools: Sequence[ToolInfo] = list(tools or [])
        self._temperature = temperature
        self._system = system_prompt or "You are a helpful, concise assistant."
        # The client is built lazily on first stream() — so just constructing an
        # agent (e.g. AgentSpec(...).build()) never needs credentials.
        self._client = client
        self._api_key = api_key
        self._base_url = base_url
        self._headers = headers
        self._history: Dict[str, List[Dict[str, str]]] = {}

    def _ensure_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as e:  # pragma: no cover
                raise ImportError(
                    "The OpenAI backend requires the 'openai' package. "
                    'Install it with: pip install "partnuh[openai]"'
                ) from e

            self._client = OpenAI(
                api_key=self._api_key or os.environ.get("OPENAI_API_KEY"),
                base_url=self._base_url,
                default_headers=self._headers,
            )
        return self._client

    def _messages(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self._history:
            self._history[session_id] = [{"role": "system", "content": self._system}]
        return self._history[session_id]

    def reset(self, session_id: str = "main_session") -> None:
        self._history.pop(session_id, None)

    def stream(self, prompt: str, session_id: str = "main_session") -> Iterator[Event]:
        messages = self._messages(session_id)
        messages.append({"role": "user", "content": prompt})
        stream = self._ensure_client().chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self._temperature,
            stream=True,
        )
        reply = ""
        for chunk in stream:
            if not chunk.choices:
                continue
            piece = getattr(chunk.choices[0].delta, "content", None)
            if piece:
                reply += piece
                yield TextDelta(piece)
        messages.append({"role": "assistant", "content": reply})


def from_openai(
    *,
    name: str,
    model: str,
    system_prompt: Optional[str] = None,
    client=None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.3,
    headers: Optional[Dict[str, str]] = None,
    tools: Optional[Sequence[ToolInfo]] = None,
) -> OpenAIChatAgent:
    """Build a CliAgent from OpenAI SDK params (set base_url for OpenRouter etc.)."""
    return OpenAIChatAgent(
        name=name,
        model=model,
        system_prompt=system_prompt,
        client=client,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        headers=headers,
        tools=tools,
    )
