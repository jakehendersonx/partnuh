# custom_agent

The same smolagents agent as `basic_agent`, but with **every look-&-feel knob
customized** — a quick tour of how to theme a partnuh CLI.

It shows partnuh's two simple objects:

1. **`CliConfig`** — a settings object. All the appearance state (prompt, cursor,
   colors, box, separator, spinners, tool markers, streaming pace) lives here.
2. **the CLI** — `partnuh.wrap(your_agent, config=...)` takes *your* agent plus
   that settings object and runs the streaming REPL.

```python
look = CliConfig(prompt_sequence="~> ", banner_box=Box.DOUBLE, ...)
partnuh.wrap(agent, name="Custom Caller", config=look)
```

Every field is optional; anything you omit keeps partnuh's default. Many fields
have presets (`Prompt`, `Cursor`, `Spinner`, `Box`, `Separator`) but any
equivalent string works too.

## Setup

```bash
cd examples/custom_agent

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.template .env        # then edit .env and add your OPENROUTER_API_KEY
```

## Run

```bash
.venv/bin/python main.py                       # interactive REPL
.venv/bin/python main.py "what is 21 + 21?"    # one-shot
```

You should see the customized look: a teal `~>` prompt, a double-lined cyan
banner box, a magenta `thinking…` spinner, `━` separators, and green
`→ calling` / `✓` tool markers.

See `main.py` for the full annotated `CliConfig`. To learn every available
field, read `CliConfig` in the partnuh source (or the root README's
"Configuring the look & feel" section).
