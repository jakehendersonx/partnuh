"""Fully-customized partnuh CLI — how to tune every knob, simply.

partnuh exposes two simple objects:

  1. CliConfig  — a settings object. All the look-&-feel state lives here.
  2. the CLI    — partnuh.wrap(your_agent, config=...) takes YOUR agent plus the
                  settings and runs the streaming REPL.

So: build your agent, describe the look in a CliConfig, hand both to partnuh.
Every field below is optional — shown here set to non-defaults so you can see
each one. Anything you omit keeps partnuh's default.
"""

import os

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

import partnuh
from partnuh import CliConfig, Box, Cursor, Prompt, Separator, Spinner

load_dotenv()


@tool
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: first integer
        b: second integer
    """
    return a + b


# 1) YOUR agent — built the normal way, partnuh isn't involved here.
model = OpenAIServerModel(
    model_id=os.environ.get("PARTNUH_MODEL", "openai/gpt-5.4-nano"),
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
agent = ToolCallingAgent(tools=[add], model=model, stream_outputs=True, max_steps=4)


# 2) YOUR settings — one object holding all the look-&-feel state.
look = CliConfig(
    # prompt & input
    prompt_sequence="~> ",            # the leading sequence (or Prompt.ARROW, etc.)
    prompt_style="fg:#00d7af",        # prompt color (prompt_toolkit syntax)
    cursor=Cursor.BEAM,               # text cursor shape
    accent_style="magenta",           # color of /commands & "Available Tools"
    # banner box
    banner_border_style="cyan",       # outline color
    banner_box=Box.DOUBLE,            # outline texture
    # separator around each response
    separator=Separator.HEAVY,        # "━" (or "=", "─", your own string)
    separator_style="cyan",
    # spinners
    thinking_spinner=Spinner.ARC, thinking_text="thinking…",
    answering_spinner=Spinner.TOGGLE, answering_text="working…",
    spinner_style="magenta",
    # streaming pace
    stream_speed=0.25,                # a gentle typewriter (0 = instant)
    # tool-call markers
    tool_call_prefix="→ calling ", tool_result_prefix="✓ ", tool_style="green",
)


# 3) Hand your agent + settings to the CLI.
if __name__ == "__main__":
    partnuh.wrap(agent, name="Custom Caller", config=look)
