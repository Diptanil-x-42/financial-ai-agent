import os
from collections.abc import AsyncIterator
from typing import Callable

from agents import Agent, Runner, TResponseInputItem
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper

# Path to the financial report file (next to the project root)
_REPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'financial_report.txt')


def _read_financial_report() -> str:
    """Read the financial report lazily (not at import time) so it always gets fresh content."""
    if os.path.exists(_REPORT_PATH):
        with open(_REPORT_PATH, "r", encoding="utf-8") as file:
            return file.read()
    return "No financial data available yet. Please run the research agent first."


# Define Spanish Agent
spanish_agent = Agent(
    name="Spanish",
    handoff_description="A Spanish-speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in Spanish.",
    ),
    model="gpt-4o-mini",
)


def _create_main_agent() -> Agent:
    """Create the main agent with fresh report data."""
    report_content = _read_financial_report()
    return Agent(
        name="Assistant",
        instructions=prompt_with_handoff_instructions(
            f"You're speaking to a human, so be polite and concise. "
            f"You are a financial expert, and your job is to discuss the report with the user.\n\n"
            f"Here is the financial report:\n{report_content}"
        ),
        model="gpt-4o-mini",
        handoffs=[spanish_agent],
    )


class MyWorkflow(VoiceWorkflowBase):
    def __init__(self, on_start: Callable[[str], None]):
        """
        Args:
            on_start: A callback that is called when the workflow starts. The transcription
                is passed in as an argument.
        """
        self._input_history: list[TResponseInputItem] = []
        self._current_agent = _create_main_agent()
        self._on_start = on_start

    async def run(self, transcription: str) -> AsyncIterator[str]:
        self._on_start(transcription)

        # Add the transcription to the input history
        self._input_history.append(
            {
                "role": "user",
                "content": transcription,
            }
        )

        # Run the agent
        result = Runner.run_streamed(self._current_agent, self._input_history)

        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            yield chunk

        # Update the input history and current agent
        self._input_history = result.to_input_list()
        self._current_agent = result.last_agent