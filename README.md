# partnuh

**Wrap your agent in a fast, streaming, multi-line terminal CLI — in one line.**

partnuh is purely the aesthetic layer. You build your agent; partnuh gives it a
nice place to talk.

```python
import partnuh

partnuh.wrap(your_agent, name="Private Caller")   # → a full streaming CLI
```

> ### Supported agents
> | Framework | Status |
> |---|---|
> | [smolagents](https://github.com/huggingface/smolagents) | ✅ supported |
>
> More frameworks coming. (No agent yet? `partnuh.wrap(partnuh.demo_agent())`
> streams a canned reply with no model or network.)

<!-- TODO: demo gif here -->

## Install

```bash
pip install "partnuh[smolagents]"
```

## Examples

- **[quickstart](examples/quickstart)** — the simplest smolagents agent in a partnuh CLI.
- **[customization](examples/customization)** — the same agent with the look fully customized (prompt, cursor, colors, box, separator, spinners).

## License

MIT
