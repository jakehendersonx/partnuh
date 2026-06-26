"""Per-invocation knobs for the CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional


@dataclass
class CliConfig:
    """Variables that alter CLI behavior for a given run.

    stream_speed: 0.0 = print as fast as tokens arrive (default, best for fast
    models); 1.0 = slow typewriter. Values in between pace the output and smooth
    out bursty network chunks.
    """

    banner: bool = True
    multiline: bool = True
    stream_speed: float = 0.0
    prompt_str: str = "▌ "
    show_tool_calls: bool = True
    # Extra slash commands: name (without leading "/") -> handler(dispatcher, args).
    commands: Optional[Dict[str, Callable]] = None
