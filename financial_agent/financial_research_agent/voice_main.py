#!/usr/bin/env python3
"""
Voice-Enabled Financial Research Agent
This version allows you to use voice commands to control the financial research workflow
"""

import asyncio
import os
import sys
from pathlib import Path

# Fix path resolution for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_path)

from agents.voice import StreamedAudioInput, VoicePipeline
from agents import Agent, Runner
from financial_research_agent.manager import FinancialResearchManager

class VoiceFinancialWorkflow:
    """Voice workflow for financial research"""
    
    def __init__(self):
        self.manager = FinancialResearchManager()
        self.current_query = None
        
        # Create voice agent
        self.voice_agent = Agent(
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
    
    async def handle_voice_command(self, transcription: str):
        """Handle voice commands and execute financial research"""
        print(f"🎯 Voice Command: {transcription}")
        
        transcription_lower = transcription.lower()
        
        if "quit" in transcription_lower or "exit" in transcription_lower:
            return "Goodbye! Thank you for using the Financial Research Agent."
        
        if "help" in transcription_lower:
            return """Available voice commands:
            - Say 'analyze [company name]' to research a company
            - Say 'report' to get the latest financial report
            - Say 'help' for this list
            - Say 'quit' to exit"""
        
        if "analyze" in transcription_lower:
            # Extract company name from command
            company = transcription_lower.replace("analyze", "").strip()
            if company:
                self.current_query = f"Write up an analysis of {company}'s most recent quarter"
                print(f"🔍 Starting financial research for: {company}")
                return f"Starting financial analysis of {company}. This will take a moment..."
            else:
                return "Please specify a company name. For example: 'analyze Apple'"
        
        if "report" in transcription_lower:
            if self.current_query:
                return "I'll generate a financial report based on your previous query."
            else:
                return "Please first analyze a company using 'analyze [company name]'"
        
        # Default response
        return "I didn't understand that command. Say 'help' for available commands."
    
    async def run_financial_research(self, query: str):
        """Run the actual financial research"""
        try:
            print(f"\n🚀 Running financial research for: {query}")
            await self.manager.run(query, None)
            return "Financial research completed! Check the generated report."
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                return "Sorry, your OpenAI API quota has been exceeded. Please add a payment method to continue."
            else:
                return f"Research failed: {error_msg}"

async def voice_financial_research():
    """Main voice-enabled financial research function"""
    
    print("🎤 Voice-Enabled Financial Research Agent")
    print("=" * 60)
    print("Voice Commands:")
    print("- 'analyze [company name]' - Research a company")
    print("- 'report' - Get latest financial report")
    print("- 'help' - Show available commands")
    print("- 'quit' - Exit the system")
    print("=" * 60)
    
    # Create workflow
    workflow = VoiceFinancialWorkflow()
    
    # Voice pipeline
    pipeline = VoicePipeline(workflow=workflow.handle_voice_command)
    audio_input = StreamedAudioInput()
    
    try:
        print("\n🎤 Starting voice pipeline...")
        print("💡 Speak clearly into your microphone")
        print("⏹️  Press Ctrl+C to stop")
        
        # Run the voice pipeline
        result = await pipeline.run(audio_input)
        
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                print(f"🔊 Audio response: {len(event.data) if event.data else 0} bytes")
            elif event.type == "voice_stream_event_lifecycle":
                print(f"📡 Status: {event.event}")
                
    except KeyboardInterrupt:
        print("\n👋 Voice session ended by user")
    except Exception as e:
        print(f"❌ Error in voice pipeline: {e}")
        print("💡 Make sure your microphone is working and OpenAI API is configured")
    finally:
        print("🔇 Voice session closed")

def check_dependencies():
    """Check if all dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check sounddevice
    try:
        import sounddevice
        print("✅ sounddevice - Available")
    except ImportError:
        print("❌ sounddevice - Missing")
        print("💡 Install: pip install sounddevice")
        return False
    
    # Check voice components
    try:
        from agents.voice import StreamedAudioInput, VoicePipeline
        print("✅ Voice components - Available")
    except ImportError:
        print("❌ Voice components - Missing")
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
    print("🎤 Voice-Enabled Financial Research Agent")
    print("=" * 60)
    
    if check_dependencies():
        print("\n🚀 All dependencies available! Starting voice system...")
        await voice_financial_research()
    else:
        print("\n❌ Missing dependencies. Please install them first.")
        print("\n📝 You can still use the text version:")
        print("   python -m financial_research_agent.main")

if __name__ == "__main__":
    asyncio.run(main())
