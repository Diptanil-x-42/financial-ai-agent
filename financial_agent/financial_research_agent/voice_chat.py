import random
from collections.abc import AsyncIterator
from typing import Callable

# Import from the src directory directly
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from agents import Agent, Runner, TResponseInputItem, function_tool
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import VoiceWorkflowBase, VoiceWorkflowHelper
import os

financial_report_path = "financial_report.txt"

# Read or initialize financial report content
if os.path.exists(financial_report_path):
    with open(financial_report_path, "r", encoding="utf-8") as file:
        financial_report_content = file.read()
else:
    print("financial_report.txt not found. It will be created after running the agent.")
    financial_report_content = "No financial data available yet."

# Define Spanish Agent
spanish_agent = Agent(
    name="Spanish",
    handoff_description="A Spanish-speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in Spanish.",
    ),
    model="gpt-4o-mini",
)

# Define Main Financial Assistant Agent
agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        f"You're speaking to a human, so be polite and concise. "
        f"You are a financial expert, and your job is to discuss the report with the user.\n\n"
        f"Here is the financial report:\n{financial_report_content}"
    ),
    model="gpt-4o-mini",
    handoffs=[spanish_agent],
)


class MyWorkflow(VoiceWorkflowBase):
    def __init__(self, secret_word: str, on_start: Callable[[str], None]):
        """
        Args:
            secret_word: The secret word to guess.
            on_start: A callback that is called when the workflow starts. The transcription
                is passed in as an argument.
        """
        self._input_history: list[TResponseInputItem] = []
        self._current_agent = agent
        self._secret_word = secret_word.lower()
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

        # If the user guessed the secret word, do alternate logic
        if self._secret_word in transcription.lower():
            yield "You guessed the secret word!"
            self._input_history.append(
                {
                    "role": "assistant",
                    "content": "You guessed the secret word!",
                }
            )
            return

        # Otherwise, run the agent
        result = Runner.run_streamed(self._current_agent, self._input_history)

        async for chunk in VoiceWorkflowHelper.stream_text_from(result):
            yield chunk

        # Update the input history and current agent
        self._input_history = result.to_input_list()
        self._current_agent = result.last_agent