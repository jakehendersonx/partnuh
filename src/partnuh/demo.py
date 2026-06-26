"""A deterministic "agent" that streams guaranteed text — no key, no network.

The CLI behaves exactly as if it were talking to a real agent, but the stream
is a fixed algorithm. Handy for trying the interface, demos, and tests.

    partnuh.wrap(partnuh.demo_agent())
"""

from __future__ import annotations

import re
from typing import Optional

from .adapters import from_callable
from .events import TextDelta

SOLILOQUY = """\
To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them. To die—to sleep,
No more; and by a sleep to say we end
The heart-ache and the thousand natural shocks
That flesh is heir to: 'tis a consummation
Devoutly to be wish'd. To die, to sleep;
To sleep, perchance to dream—ay, there's the rub:
For in that sleep of death what dreams may come,
When we have shuffled off this mortal coil,
Must give us pause."""


def demo_agent(
    script: Optional[str] = None,
    *,
    name: str = "Demo",
    model: str = "demo",
    echo_prompt: bool = False,
):
    """A deterministic CliAgent that streams `script` word-by-word.

    Defaults to Hamlet's soliloquy. With ``echo_prompt=True`` it prefixes each
    reply with what you typed. No API key or network involved.
    """
    text = SOLILOQUY if script is None else script

    def _stream(prompt: str, session_id: str):
        if echo_prompt:
            yield TextDelta(f"You said: {prompt}\n\n")
        # \S+\s* keeps each word with its trailing whitespace, so newlines and
        # spacing in `text` are preserved as it streams.
        for token in re.findall(r"\S+\s*", text):
            yield TextDelta(token)

    return from_callable(_stream, name=name, model=model)
