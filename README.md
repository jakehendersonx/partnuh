# partnuh

**A streaming terminal REPL for any agent.**

`partnuh` is purely aesthetic: it's the fast, multi-line, token-streaming
terminal REPL. You build your agent with its own dependencies — smolagents, an
OpenAI-compatible chat model, anything — and hand it to `partnuh.run()`, which
auto-wraps it. partnuh never builds agents and imports no framework of its own.

```python
import partnuh
from smolagents import ToolCallingAgent, OpenAIServerModel

agent = ToolCallingAgent(tools=[...], model=OpenAIServerModel(...))  # your agent
partnuh.wrap(agent, name="Private Caller").run()                     # one line → a full CLI
```

## Run the example locally (from a checkout)

Install the package into a virtualenv in editable mode, then run the example —
`examples/basic_agent.py`, a complete agent CLI in a few lines:

```bash
cd partnuh
python3 -m venv .venv
.venv/bin/pip install -e ".[smolagents,dotenv]"   # or ".[all]"
cp .env.template .env                              # add your OPENROUTER_API_KEY

.venv/bin/python examples/basic_agent.py             # interactive
.venv/bin/python examples/basic_agent.py "21 + 21?"  # one-shot
```

It auto-loads `.env`. See the comments in the file for how each part maps to the
library.

## Install (as a dependency)

```bash
pip install partnuh                 # core (bring your own agent)
pip install "partnuh[openai]"       # + OpenAI/OpenRouter chat backend
pip install "partnuh[smolagents]"   # + smolagents adapter
pip install "partnuh[all]"
```

## Use

**Bring your own agent.** Build it however you like, then `partnuh.run()` it.
What you pass is auto-wrapped: an already-`CliAgent`, a smolagents agent, or a
plain stream function all just work.

```python
import os, partnuh
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

@tool
def add(a: int, b: int) -> int:
    "Add two integers.\n\nArgs:\n  a: first\n  b: second"
    return a + b

model = OpenAIServerModel(model_id="openai/gpt-5.4-nano",
                          api_base="https://openrouter.ai/api/v1",
                          api_key=os.environ["OPENROUTER_API_KEY"])
agent = ToolCallingAgent(tools=[add], model=model, stream_outputs=True)

partnuh.wrap(agent, name="Private Caller").run()   # auto-wrapped; no partnuh agent type to learn
```

`wrap()` returns a configurable `Cli`; `.run()` launches it. Configure it with
`CliConfig` fields as keyword overrides:

```python
partnuh.wrap(agent, name="Private Caller", prompt_str="❯ ", stream_speed=0.3).run()
```

(`partnuh.run(agent, ...)` is shorthand for `wrap(agent, ...).run()`.)

**Anything is an agent** — a generator function is enough (no key, no framework):

```python
import partnuh
from partnuh import TextDelta

def echo(prompt, session_id):
    for word in f"you said: {prompt}".split(" "):
        yield TextDelta(word + " ")

partnuh.wrap(echo, name="Echo").run()
```

**Optional sugar:** for the no-framework chat case there's `AgentSpec`, a thin
helper over the OpenAI/OpenRouter backend. It's convenience only — partnuh
doesn't need it.

```python
agent = partnuh.AgentSpec(name="Private Caller", model="openai/gpt-5.4-nano").build()
partnuh.wrap(agent).run()
```

## In the REPL

- **Enter** submits, **Shift+Enter** inserts a newline (works across terminals
  — see below). Backspace on a blank line joins back to the previous line.
- `/tools` list tools · `/reset` clear history · `/help` · `/quit`

## Configuring behavior

```python
from partnuh import CliConfig

partnuh.run(agent, config=CliConfig(
    stream_speed=0.0,      # 0 = as-fast-as-tokens-arrive; 1.0 = slow typewriter
    show_tool_calls=True,  # render the tool-call markers
    banner=True,
    commands={"clear": lambda d, args: __import__("os").system("clear")},
))
```

## How it works (ports & adapters)

There is no universal in-process agent object shared across frameworks, so
`partnuh` defines a tiny contract and ships adapters:

- **`CliAgent`** protocol — `name`, `model`, `tools`, and
  `stream(prompt, session_id) -> Iterator[Event]`.
- **`Event`** union — `TextDelta`, `ToolCallStarted`, `ToolResult`, `Error`,
  `Done`. Every adapter translates its framework's native stream into these; a
  bare `str` is treated as a `TextDelta`.
- **Adapters** — `from_openai`, `from_smolagents`, `from_callable`. Add your own
  by yielding `Event`s.
- **`Pacer`** — renders the event stream to the terminal with optional speed
  control.

### The Shift+Enter trick

Terminals encode Shift+Enter differently, and prompt_toolkit's default collapses
the common Ghostty/xterm encoding into plain Enter (so it submits instead of
adding a newline). `partnuh` registers every known Shift+Enter escape sequence
(`\x1b[27;2;13~`, kitty's `\x1b[13;2u`, …) and maps it to "insert newline" — no
terminal config required.

## License

MIT
