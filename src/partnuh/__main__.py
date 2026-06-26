"""`partnuh` console entry point — a ready-to-run chat over OpenRouter.

    export OPENROUTER_API_KEY=sk-or-...
    partnuh                       # interactive
    partnuh "what's 2+2?"         # one-shot
    PARTNUH_MODEL=openai/gpt-5-nano partnuh

This is a convenience demo of the library; for real use, import partnuh and
build your own agent/spec.
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    # Optional .env convenience if python-dotenv is installed.
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY not set.", file=sys.stderr)
        print("  export OPENROUTER_API_KEY=sk-or-...", file=sys.stderr)
        sys.exit(1)

    from .spec import AgentSpec
    from .cli import wrap

    model = os.environ.get("PARTNUH_MODEL", "openai/gpt-5.4-nano")
    agent = AgentSpec(name="partnuh", model=model, backend="openrouter").build()
    wrap(agent)


if __name__ == "__main__":
    main()
