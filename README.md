# partnuh

**A streaming terminal REPL for any agent.**

`partnuh` gives an existing agent — smolagents, an OpenAI-compatible chat model,
or anything you can wrap — a fast, multi-line terminal chat with token
streaming. It doesn't build agents; it gives the one you have a nice place to
talk.

```python
import partnuh

agent = partnuh.AgentSpec(name="Private Caller", model="openai/gpt-5.4-nano").build()
partnuh.run(agent)
```

## Install

```bash
pip install partnuh                 # core (bring your own agent)
pip install "partnuh[openai]"       # + OpenAI/OpenRouter chat backend
pip install "partnuh[smolagents]"   # + smolagents adapter
pip install "partnuh[all]"
```

## Use

**A chat model over OpenRouter** (no framework):

```python
import partnuh

agent = partnuh.AgentSpec(
    name="Private Caller",
    model="openai/gpt-5.4-nano",     # OpenRouter model id
    backend="openrouter",            # uses $OPENROUTER_API_KEY
).build()
partnuh.run(agent)
```

**Wrap a smolagents agent** (tool calling works):

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
smol = ToolCallingAgent(tools=[add], model=model, stream_outputs=True)

agent = partnuh.from_smolagents(smol, name="Private Caller")
partnuh.run(agent)
```

**Ready-to-run command** (after `pip install "partnuh[openai,dotenv]"`):

```bash
export OPENROUTER_API_KEY=sk-or-...
partnuh                       # interactive
partnuh "what's 2+2?"         # one-shot
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
