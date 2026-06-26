"""Input key handling for the multi-line REPL.

The hard part is making Shift+Enter insert a newline (vs. submit) across
terminals. Terminals encode Shift+Enter differently, and prompt_toolkit ships a
default that collapses the common Ghostty/xterm encoding into plain Enter. We
override the known encodings to Control-J (LF), which we bind to "insert
newline". Because these escape sequences are unambiguous, registering all of
them at once is the auto-detect: it just works wherever you run.

Backspace-on-a-blank-line joining back to the previous line is prompt_toolkit's
default multiline behavior (Backspace deletes the preceding char, including a
newline), so it needs no special binding.
"""

from __future__ import annotations

from typing import Sequence

from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.input.ansi_escape_sequences import ANSI_SEQUENCES
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

DEFAULT_NEWLINE_KEYS = ("s-enter", "c-enter", "a-enter", "c-j")

# Known Shift+Enter encodings -> treat as Control-J (newline insert).
SHIFT_ENTER_SEQUENCES = (
    "\x1b[27;2;13~",  # xterm "modifyOtherKeys" (Ghostty and others)
    "\x1b[13;2u",     # kitty keyboard protocol (CSI u)
)


def register_shift_enter() -> None:
    """Map every known Shift+Enter sequence to Control-J. Idempotent."""
    for seq in SHIFT_ENTER_SEQUENCES:
        ANSI_SEQUENCES[seq] = Keys.ControlJ


def build_key_bindings(newline_keys: Sequence[str] = DEFAULT_NEWLINE_KEYS) -> KeyBindings:
    register_shift_enter()
    kb = KeyBindings()
    menu_visible = Condition(lambda: get_app().current_buffer.complete_state is not None)

    @kb.add("enter", filter=menu_visible)
    def _(event):
        b = event.current_buffer
        if b.complete_state:
            if b.complete_state.current_completion is None:
                b.complete_next()
            if b.complete_state and b.complete_state.current_completion:
                b.apply_completion(b.complete_state.current_completion)

    @kb.add("enter", filter=~menu_visible)
    def _(event):
        if event.app.current_buffer.document.text.strip():
            event.app.current_buffer.validate_and_handle()

    @kb.add("down", filter=menu_visible)
    def _(event):
        event.current_buffer.complete_next()

    @kb.add("up", filter=menu_visible)
    def _(event):
        event.current_buffer.complete_previous()

    @kb.add("tab")
    def _(event):
        event.current_buffer.complete_next()

    @kb.add("s-tab")
    def _(event):
        event.current_buffer.complete_previous()

    # Configured newline keys all insert a newline (default: Shift/Ctrl/Alt-Enter
    # and Control-J, which is what the Shift+Enter sequences map to).
    for key in newline_keys:
        try:
            @kb.add(key)
            def _(event):
                event.current_buffer.insert_text("\n")
        except Exception:
            pass

    @kb.add("c-q")
    def _(event):
        event.app.exit(exception=EOFError)

    @kb.add("c-c")
    def _(event):
        event.app.exit(exception=KeyboardInterrupt)

    return kb
