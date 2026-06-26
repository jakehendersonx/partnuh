"""Named presets for the look & feel knobs.

These are plain string constants, not strict enums — every field that takes one
also accepts your own value. They exist for discoverability/autocomplete:

    partnuh.wrap(agent, prompt_sequence=partnuh.Prompt.ARROW, cursor=partnuh.Cursor.BEAM)
    partnuh.wrap(agent, prompt_sequence="~> ")   # your own works just as well
"""

from __future__ import annotations


class Prompt:
    """Leading sequence printed before your input."""
    BAR = "▌ "
    ARROW = "❯ "
    CHEVRON = "> "
    DOUBLE = "» "
    DOT = "• "
    DOLLAR = "$ "
    STAR = "✦ "


class Cursor:
    """Text-cursor shape in the input line."""
    BLOCK = "block"
    BEAM = "beam"
    UNDERLINE = "underline"
    BLINKING_BLOCK = "blinking-block"
    BLINKING_BEAM = "blinking-beam"
    BLINKING_UNDERLINE = "blinking-underline"


class Spinner:
    """Spinner animations (any rich spinner name also works)."""
    DOTS = "dots"
    LINE = "line"
    ARC = "arc"
    STAR = "star"
    TOGGLE = "toggle"
    POINT = "point"
    CIRCLE = "circle"
    BOUNCING_BAR = "bouncingBar"
    BOUNCING_BALL = "bouncingBall"
    AESTHETIC = "aesthetic"


class Box:
    """Banner outline texture."""
    ROUNDED = "rounded"
    SQUARE = "square"
    DOUBLE = "double"
    HEAVY = "heavy"
    ASCII = "ascii"
    MINIMAL = "minimal"
    SIMPLE = "simple"
    HORIZONTALS = "horizontals"
    NONE = "none"


class Separator:
    """The divider drawn around each response (repeated to fill the width)."""
    DASH = "-"
    LINE = "─"
    HEAVY = "━"
    DOT = "·"
    EQUALS = "="
    TILDE = "~"
    DOUBLE = "═"
