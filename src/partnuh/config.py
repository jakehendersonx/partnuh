"""CliConfig — everything you can tune about a partnuh CLI's look and feel.

Every field has a sensible default (the look partnuh ships with). Pass a
CliConfig to `wrap(..., config=...)`, or override individual fields as keyword
args: `partnuh.wrap(agent, prompt_sequence="❯ ", stream_speed=0.3)`.

Many fields accept a `presets` constant (Prompt, Cursor, Spinner, Box,
Separator) for discoverability, but any equivalent string works too.

Note on style strings: `prompt_style` uses prompt_toolkit syntax ("fg:#888888");
all other *_style fields are rendered by rich, so they use rich syntax
("cyan", "dim", "bold #00afff").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

from .presets import Box, Cursor, Prompt, Separator, Spinner


@dataclass
class CliConfig:
    # --- prompt & input appearance ------------------------------------------
    prompt_sequence: str = Prompt.BAR          # leading sequence before your input
    prompt_style: str = "fg:#888888"           # prompt_toolkit style for the prompt
    cursor: Optional[str] = None               # Cursor.* or None (terminal default)
    accent_style: str = "cyan"                 # color of /commands & special keywords

    # --- banner box ---------------------------------------------------------
    banner: bool = True
    banner_border_style: str = "dim"           # outline color
    banner_box: str = Box.ROUNDED              # outline texture
    banner_label_style: str = "dim"            # color of the name:/model:/tools: labels

    # --- response separator -------------------------------------------------
    show_dividers: bool = True
    separator: str = Separator.DASH            # repeated to fill the width
    separator_style: str = "dim"

    # --- input keys ---------------------------------------------------------
    multiline: bool = True
    newline_keys: Tuple[str, ...] = ("s-enter", "c-enter", "a-enter", "c-j")

    # --- streaming output ---------------------------------------------------
    # stream_speed: 0.0 = as fast as tokens arrive; 1.0 = slow typewriter.
    # token_delay: explicit seconds-per-character; if set, it wins over stream_speed.
    stream_speed: float = 0.0
    token_delay: Optional[float] = None

    # --- spinners -----------------------------------------------------------
    thinking_spinner: str = Spinner.DOTS       # shown until the first token arrives
    thinking_text: str = "Thinking..."
    answering_spinner: Optional[str] = Spinner.DOTS  # shown while a tool runs / next step composes
    answering_text: str = "Working..."
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
