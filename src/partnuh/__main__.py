"""`partnuh` console entry point — a no-setup demo of the CLI.

    partnuh                 # interactive
    partnuh "hi"            # one-shot

Runs the offline demo agent (deterministic, no key, no network) so you can see
the interface. For real use, import partnuh and wrap your own agent:

    import partnuh
    partnuh.wrap(your_agent, name="...")
"""

from __future__ import annotations


def main() -> None:
    from .cli import wrap
    from .demo import demo_agent

    wrap(demo_agent(name="partnuh"))


if __name__ == "__main__":
    main()
