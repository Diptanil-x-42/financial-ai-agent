#!/usr/bin/env python3
"""
Voice-Enabled Financial Research Agent
This version allows you to interact with the financial agent using voice commands
"""

import asyncio
import os

from agents.voice import StreamedAudioInput, VoicePipeline
from financial_research_agent.voice_chat import MyWorkflow


async def voice_financial_research():
    """Run the financial research agent with voice interaction"""

    print("Voice: Voice-Enabled Financial Research Agent")
    print("=" * 50)
    print("Commands:")
    print("- Say 'analyze [company name]' to research a company")
    print("- Say 'report' to get the latest financial report")
    print("- Say 'quit' to exit")
    print("=" * 50)

    # Create voice pipeline
    workflow = MyWorkflow(
        on_start=lambda transcription: print(f"Heard: You said: {transcription}")
    )

    pipeline = VoicePipeline(workflow=workflow)
    audio_input = StreamedAudioInput()

    try:
        print("\nVoice: Starting voice pipeline...")
        print("Tip: Speak clearly into your microphone")

        # Run the voice pipeline
        result = await pipeline.run(audio_input)

        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                # Handle audio output (TTS)
                print(f"Audio: Audio response received: {len(event.data) if event.data else 0} bytes")
            elif event.type == "voice_stream_event_lifecycle":
                print(f"Status: Lifecycle: {event.event}")

    except KeyboardInterrupt:
        print("\nGoodbye: Voice session ended by user")
    except Exception as e:
        print(f"[ERROR] Error in voice pipeline: {e}")
        print("Tip: Make sure your microphone is working and OpenAI API is configured")
    finally:
        print("Closed: Voice session closed")


def _run_text_fallback():
    """Run the text-based version as a fallback (in a new event loop)."""
    print("\nText: Falling back to text-based version...")
    try:
        from financial_research_agent.main import main
        asyncio.run(main())
    except Exception as e:
        print(f"[ERROR] Text version also failed: {e}")


async def main():
    """Main entry point with fallback options"""

    # Check if voice dependencies are available
    try:
        import sounddevice
        print("[OK] Audio dependencies available")
    except ImportError:
        print("[ERROR] Audio dependencies not available")
        print("Tip: Install with: pip install sounddevice")
        # Call fallback synchronously - safe because we haven't started voice yet
        _run_text_fallback()
        return

    # Check if OpenAI API is working
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not set")
        print("Tip: Set your API key: $env:OPENAI_API_KEY='your-key-here'")
        return

    print("[OK] OpenAI API key configured")

    # Try voice first
    try:
        await voice_financial_research()
    except Exception as e:
        print(f"[ERROR] Voice failed: {e}")
        print("Tip: Falling back to text version...")
        # Use a separate thread for the fallback to avoid asyncio.run() inside a running loop
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await asyncio.get_event_loop().run_in_executor(pool, _run_text_fallback)


if __name__ == "__main__":
    asyncio.run(main())
