# basic_agent

The simplest partnuh starter: a [smolagents](https://github.com/huggingface/smolagents)
tool-calling agent running in partnuh's streaming terminal CLI.

`main.py` builds the agent the normal smolagents way and hands it to
`partnuh.wrap(agent)` — one line, you get the whole streaming CLI. partnuh is
only the aesthetic layer; there's no partnuh-specific agent type to learn.

## Setup

```bash
cd examples/basic_agent

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.template .env        # then edit .env and add your OPENROUTER_API_KEY
```

Get an OpenRouter key at https://openrouter.ai/keys.

## Run

```bash
.venv/bin/python main.py                 # interactive REPL
.venv/bin/python main.py "what is 21 + 21?"   # one-shot
```

In the REPL: **Enter** submits, **Shift+Enter** adds a newline. Commands:
`/tools`, `/reset`, `/help`, `/quit`.

## Verify it works

Ask it something that forces the tool:

```
▌ what is 100 + 23? use the add tool
```

You should see partnuh render the tool call and the answer, e.g.:

```
⚙ add(a=100, b=23)
→ 123
123
```

The `⚙`/`→` lines are partnuh showing the agent's tool call and result; the
final `123` is the answer. If you see that, the agent + partnuh + OpenRouter are
all wired up correctly.
