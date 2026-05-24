#!/usr/bin/env python3
"""
Voice-Enabled Financial Research Agent
This version allows you to use voice commands to control the financial research workflow
"""

import asyncio
import os
from collections.abc import AsyncIterator
from typing import Callable

from agents.voice import StreamedAudioInput, VoicePipeline, VoiceWorkflowBase, VoiceWorkflowHelper
from agents import Agent, Runner, TResponseInputItem
from financial_research_agent.manager import FinancialResearchManager


class VoiceFinancialWorkflow(VoiceWorkflowBase):
    """Voice workflow for financial research using proper VoiceWorkflowBase."""

    def __init__(self, on_start: Callable[[str], None]):
        self.manager = FinancialResearchManager()
        self._input_history: list[TResponseInputItem] = []
        self._on_start = on_start

        # Create voice agent
        self._current_agent = Agent(
            name="Financial Voice Assistant",
            instructions="""You are a financial research voice assistant.
            Keep responses short and conversational.
            Available commands:
            - 'analyze [company name]' - Research a company
            - 'report' - Get latest financial report
            - 'help' - Show available commands
            - 'quit' - Exit the system""",
            model="gpt-4o-mini"
        )

    async def run(self, transcription: str) -> AsyncIterator[str]:
        """Handle voice input and yield text responses."""
        self._on_start(transcription)

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


async def voice_financial_research():
    """Main voice-enabled financial research function"""

    print("Voice: Voice-Enabled Financial Research Agent")
    print("=" * 60)
    print("Voice Commands:")
    print("- 'analyze [company name]' - Research a company")
    print("- 'report' - Get latest financial report")
    print("- 'help' - Show available commands")
    print("- 'quit' - Exit the system")
    print("=" * 60)

    # Create workflow using proper VoiceWorkflowBase subclass
    workflow = VoiceFinancialWorkflow(
        on_start=lambda t: print(f"Heard: You said: {t}")
    )

    # Voice pipeline
    pipeline = VoicePipeline(workflow=workflow)
    audio_input = StreamedAudioInput()

    try:
        print("\nVoice: Starting voice pipeline...")
        print("Tip: Speak clearly into your microphone")
        print("Stop:  Press Ctrl+C to stop")

        # Run the voice pipeline
        result = await pipeline.run(audio_input)

        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                print(f"Audio: Audio response: {len(event.data) if event.data else 0} bytes")
            elif event.type == "voice_stream_event_lifecycle":
                print(f"Status: Status: {event.event}")

    except KeyboardInterrupt:
        print("\nGoodbye: Voice session ended by user")
    except Exception as e:
        print(f"[ERROR] Error in voice pipeline: {e}")
        print("Tip: Make sure your microphone is working and OpenAI API is configured")
    finally:
        print("Closed: Voice session closed")

def check_dependencies():
    """Check if all dependencies are available"""
    print("Checking: Checking dependencies...")

    # Check sounddevice
    try:
        import sounddevice
        print("[OK] sounddevice - Available")
    except ImportError:
        print("[ERROR] sounddevice - Missing")
        print("Tip: Install: pip install sounddevice")
        return False

    # Check voice components
    try:
        from agents.voice import StreamedAudioInput, VoicePipeline
        print("[OK] Voice components - Available")
    except ImportError:
        print("[ERROR] Voice components - Missing")
        return False

    # Check OpenAI API
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("[OK] OpenAI API Key - Configured")
    else:
        print("[ERROR] OpenAI API Key - Not set")
        print("Tip: Set with: $env:OPENAI_API_KEY='your-key-here'")
        return False

    return True

async def main():
    """Main entry point"""
    print("Voice: Voice-Enabled Financial Research Agent")
    print("=" * 60)

    if check_dependencies():
        print("\nStarting: All dependencies available! Starting voice system...")
        await voice_financial_research()
    else:
        print("\n[ERROR] Missing dependencies. Please install them first.")
        print("\nText: You can still use the text version:")
        print("   python -m financial_research_agent.main")

if __name__ == "__main__":
    asyncio.run(main())
