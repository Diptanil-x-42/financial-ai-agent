#!/usr/bin/env python3
"""
Simple Voice Demo for Financial Agent
This demonstrates basic voice input/output functionality
"""

import asyncio
import os
import sys

from agents.voice import StreamedAudioInput, VoicePipeline
from agents import Agent, Runner


async def simple_voice_demo():
    """Simple voice demo with basic commands"""

    print("Voice: Simple Voice Demo")
    print("=" * 40)
    print("Voice Commands:")
    print("- 'hello' - Get a greeting")
    print("- 'time' - Get current time")
    print('- "analyze apple" - Financial analysis')
    print("- 'quit' - Exit the demo")
    print("=" * 40)

    try:
        # Create a simple agent for voice interaction
        voice_agent = Agent(
            name="Voice Assistant",
            instructions="""You are a helpful voice assistant. Keep responses short and conversational.
            When asked about financial analysis, provide brief insights.
            Always respond in a friendly, helpful manner.""",
            model="gpt-4o-mini"
        )

        # Simple workflow
        async def simple_workflow(transcription: str):
            print(f"Heard: You said: {transcription}")

            if "quit" in transcription.lower():
                return "Goodbye! Have a great day!"

            # Run the agent with the transcription
            result = await Runner.run(voice_agent, transcription)
            response = str(result.final_output)
            print(f"Assistant: Assistant: {response}")
            return response

        # Create voice pipeline
        pipeline = VoicePipeline(workflow=simple_workflow)
        audio_input = StreamedAudioInput()

        print("\nVoice: Starting voice demo...")
        print("Tip: Speak into your microphone")
        print("Stop:  Press Ctrl+C to stop")

        # Run the pipeline
        result = await pipeline.run(audio_input)

        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                print(f"Audio: Audio response: {len(event.data) if event.data else 0} bytes")
            elif event.type == "voice_stream_event_lifecycle":
                print(f"Status: Status: {event.event}")

    except ImportError as e:
        print(f"[ERROR] Missing voice dependencies: {e}")
        print(f"Tip: Install: pip install sounddevice numpy")
    except Exception as e:
        print(f"[ERROR] Voice demo failed: {e}")
        print("Tip: Check your microphone and OpenAI API configuration")

def check_dependencies():
    """Check if voice dependencies are available"""
    print("Checking: Checking voice dependencies...")

    # Check sounddevice
    try:
        import sounddevice
        print("[OK] sounddevice - Available")
    except ImportError:
        print("[ERROR] sounddevice - Missing")
        print("Tip: Install: pip install sounddevice")
        return False

    # Check local voice components
    try:
        from agents.voice import StreamedAudioInput, VoicePipeline
        print("[OK] Local voice components - Available")
    except ImportError as e:
        print(f"[ERROR] Local voice components - Missing: {e}")
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
    print("Voice: Financial Agent Voice Demo")
    print("=" * 40)

    if check_dependencies():
        print("\nStarting: All dependencies available! Starting voice demo...")
        await simple_voice_demo()
    else:
        print("\n[ERROR] Missing dependencies. Please install them first.")
        print("\nText: You can still use the text version:")
        print("   python -m financial_research_agent.main")

if __name__ == "__main__":
    asyncio.run(main())
