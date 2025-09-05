#!/usr/bin/env python3
"""
Simple Voice Demo for Financial Agent
This demonstrates basic voice input/output functionality
"""

import asyncio
import os
import sys

# Add src directory to path - fix the path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_path)

async def simple_voice_demo():
    """Simple voice demo with basic commands"""
    
    print("🎤 Simple Voice Demo")
    print("=" * 40)
    print("Voice Commands:")
    print("- 'hello' - Get a greeting")
    print("- 'time' - Get current time")
    print('- "analyze apple" - Financial analysis')
    print("- 'quit' - Exit the demo")
    print("=" * 40)
    
    try:
        # Import from local src/agents directory
        from agents.voice import StreamedAudioInput, VoicePipeline
        from agents import Agent, Runner
        
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
            print(f"🎯 You said: {transcription}")
            
            if "quit" in transcription.lower():
                return "Goodbye! Have a great day!"
            
            # Run the agent with the transcription
            result = await Runner.run(voice_agent, transcription)
            response = result.final_output.content
            print(f"🤖 Assistant: {response}")
            return response
        
        # Create voice pipeline
        pipeline = VoicePipeline(workflow=simple_workflow)
        audio_input = StreamedAudioInput()
        
        print("\n🎤 Starting voice demo...")
        print("💡 Speak into your microphone")
        print("⏹️  Press Ctrl+C to stop")
        
        # Run the pipeline
        result = await pipeline.run(audio_input)
        
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                print(f"🔊 Audio response: {len(event.data) if event.data else 0} bytes")
            elif event.type == "voice_stream_event_lifecycle":
                print(f"📡 Status: {event.event}")
                
    except ImportError as e:
        print(f"❌ Missing voice dependencies: {e}")
        print(f"💡 Current path: {os.getcwd()}")
        print(f"💡 Added path: {src_path}")
        print(f"💡 Python path: {sys.path[:3]}")
    except Exception as e:
        print(f"❌ Voice demo failed: {e}")
        print("💡 Check your microphone and OpenAI API configuration")

def check_dependencies():
    """Check if voice dependencies are available"""
    print("🔍 Checking voice dependencies...")
    
    # Check sounddevice
    try:
        import sounddevice
        print("✅ sounddevice - Available")
    except ImportError:
        print("❌ sounddevice - Missing")
        print("💡 Install: pip install sounddevice")
        return False
    
    # Check local voice components
    try:
        # Use the same path resolution as above
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(current_dir, '..', 'src')
        sys.path.insert(0, src_path)
        
        from agents.voice import StreamedAudioInput, VoicePipeline
        print("✅ Local voice components - Available")
    except ImportError as e:
        print(f"❌ Local voice components - Missing: {e}")
        print(f"💡 Tried path: {src_path}")
        return False
    
    # Check OpenAI API
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OpenAI API Key - Configured")
    else:
        print("❌ OpenAI API Key - Not set")
        print("💡 Set with: $env:OPENAI_API_KEY='your-key-here'")
        return False
    
    return True

async def main():
    """Main entry point"""
    print("🎤 Financial Agent Voice Demo")
    print("=" * 40)
    
    if check_dependencies():
        print("\n🚀 All dependencies available! Starting voice demo...")
        await simple_voice_demo()
    else:
        print("\n❌ Missing dependencies. Please install them first.")
        print("\n📝 You can still use the text version:")
        print("   python -m financial_research_agent.main")

if __name__ == "__main__":
    asyncio.run(main())
