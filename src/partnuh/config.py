"""CliConfig — everything you can tune about a partnuh CLI's look and feel.

Every field has a sensible default (the look partnuh ships with). Pass a
CliConfig to `wrap(..., config=...)`, or override individual fields as keyword
args: `partnuh.wrap(agent, prompt_str="❯ ", stream_speed=0.3)`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple


@dataclass
class CliConfig:
    # --- prompt & appearance ------------------------------------------------
    prompt_str: str = "▌ "                 # the leading character(s) before your input
    prompt_style: str = "fg:#888888"       # prompt_toolkit style for the prompt
    cursor_shape: Optional[str] = None     # "block" | "beam" | "underline" |
    #                                        "blinking-block" | "blinking-beam" |
    #                                        "blinking-underline" | None (terminal default)
    banner: bool = True                    # show the startup info panel
    show_dividers: bool = True             # the dashed rule around each response

    # --- input --------------------------------------------------------------
    multiline: bool = True
    newline_keys: Tuple[str, ...] = ("s-enter", "c-enter", "a-enter", "c-j")

    # --- streaming output ---------------------------------------------------
    # stream_speed: 0.0 = as fast as tokens arrive; 1.0 = slow typewriter.
    # token_delay: explicit seconds-per-character; if set, it wins over stream_speed.
    stream_speed: float = 0.0
    token_delay: Optional[float] = None

    # --- spinner (shown until the first token arrives) ----------------------
    spinner: str = "dots"
    spinner_text: str = "Thinking..."
    spinner_style: str = "dim"

    # --- tool-call rendering ------------------------------------------------
    show_tool_calls: bool = True
    tool_call_prefix: str = "⚙ "
    tool_result_prefix: str = "→ "
    tool_style: str = "dim"

    # --- commands -----------------------------------------------------------
    # Extra slash commands: name (without leading "/") -> handler(dispatcher, args).
    commands: Optional[Dict[str, Callable]] = None

    def resolved_token_delay(self) -> float:
        """Seconds per character to pace output at (0 = instant)."""
        if self.token_delay is not None:
            return max(0.0, self.token_delay)
        return max(0.0, min(1.0, self.stream_speed)) * 0.04
