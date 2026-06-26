# partnuh

**A streaming terminal REPL for any agent.**

`partnuh` is purely aesthetic: it's the fast, multi-line, token-streaming
terminal REPL. You build your agent with its own dependencies — smolagents, an
OpenAI-compatible chat model, anything — and hand it to `partnuh.wrap()`, which
auto-wraps it. partnuh never builds agents and imports no framework of its own.

```python
import partnuh
from smolagents import ToolCallingAgent, OpenAIServerModel

agent = ToolCallingAgent(tools=[...], model=OpenAIServerModel(...))  # your agent
partnuh.wrap(agent, name="Private Caller")                           # one line → a full CLI
```

## Examples

Each example is a self-contained project (its own `requirements.txt` and
`README.md`):

| example | shows |
|---|---|
| [`examples/basic_agent`](examples/basic_agent) | the simplest starter — a smolagents agent in a partnuh CLI |
| [`examples/custom_agent`](examples/custom_agent) | the same agent with every look-&-feel knob customized |

```bash
cd examples/basic_agent
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.template .env            # add your OPENROUTER_API_KEY
.venv/bin/python main.py
```

## Install (as a dependency)

```bash
pip install partnuh                 # core (bring your own agent)
pip install "partnuh[openai]"       # + OpenAI/OpenRouter chat backend
pip install "partnuh[smolagents]"   # + smolagents adapter
pip install "partnuh[all]"
```

## Use

**Bring your own agent, then `wrap()` it — one line, you get the whole CLI.**
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

partnuh.wrap(agent, name="Private Caller")   # auto-wrapped + launched; that's it
```

`wrap()` launches an interactive REPL (or runs one-shot if a `prompt`/CLI args
are present). Tune the look with any `CliConfig` field as a keyword override:

```python
partnuh.wrap(agent, name="Private Caller", prompt_sequence="❯ ", stream_speed=0.3)
```

Want the object without launching (to embed or test)? Use `partnuh.Cli(...)` and
call `.start()` yourself.

**Anything is an agent** — a generator function is enough (no key, no framework):

```python
import partnuh
from partnuh import TextDelta

def echo(prompt, session_id):
    for word in f"you said: {prompt}".split(" "):
        yield TextDelta(word + " ")

partnuh.wrap(echo, name="Echo")
```

**Optional sugar:** for the no-framework chat case there's `AgentSpec`, a thin
helper over the OpenAI/OpenRouter backend. It's convenience only — partnuh
doesn't need it.

```python
agent = partnuh.AgentSpec(name="Private Caller", model="openai/gpt-5.4-nano").build()
partnuh.wrap(agent)
```

## In the REPL

- **Enter** submits, **Shift+Enter** inserts a newline (works across terminals
  — see below). Backspace on a blank line joins back to the previous line.
- `/tools` list tools · `/reset` clear history · `/help` · `/quit`

## Configuring the look & feel

Every appearance knob lives on `CliConfig`. Pass individual fields straight to
`wrap()` (they override the defaults), or build a whole `CliConfig`. Many fields
have named presets (`partnuh.Prompt`, `Cursor`, `Spinner`, `Box`, `Separator`)
for discoverability — but any equivalent string works too.

```python
import partnuh
from partnuh import Prompt, Cursor, Spinner, Box, Separator

partnuh.wrap(
    agent,
    name="Private Caller",
    # prompt & input appearance
    prompt_sequence=Prompt.ARROW,   # leading sequence "❯ " (default Prompt.BAR "▌ ")
    prompt_style="fg:#888888",      # prompt_toolkit style for the prompt
    cursor=Cursor.BEAM,             # block | beam | underline | blinking-* | None
    accent_style="cyan",            # color of /commands & special keywords
    # banner box
    banner=True,
    banner_border_style="dim",      # outline color
    banner_box=Box.ROUNDED,         # outline texture (square/double/heavy/ascii/...)
    # separator around each response
    show_dividers=True,
    separator=Separator.DASH,       # repeated to fill width ("─", "━", "=", ...)
    separator_style="dim",
    # input keys
    newline_keys=("s-enter", "c-enter", "a-enter", "c-j"),
    # streaming
    stream_speed=0.0,               # 0 = as-fast-as-tokens; 1.0 = slow typewriter
    token_delay=None,               # explicit seconds/char; overrides stream_speed
    # spinners
    thinking_spinner=Spinner.DOTS, thinking_text="Thinking...",   # until first token
    answering_spinner=Spinner.DOTS, answering_text="Working...",  # while a tool runs / next step
    spinner_style="dim",
    # tool-call markers
    show_tool_calls=True, tool_call_prefix="⚙ ", tool_result_prefix="→ ", tool_style="dim",
    # extra slash commands
    commands={"clear": lambda d, args: __import__("os").system("clear")},
)
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
