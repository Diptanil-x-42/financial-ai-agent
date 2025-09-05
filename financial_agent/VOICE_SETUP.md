# 🎤 Voice-Enabled Financial Research Agent

This guide explains how to enable and use voice functionality in your Financial Research Agent.

## 🚀 Quick Start

### 1. Basic Voice Demo
```bash
python financial_research_agent/voice_demo.py
```

### 2. Full Voice-Enabled Financial Agent
```bash
python financial_research_agent/voice_main.py
```

## 📋 Prerequisites

### Required Dependencies
- ✅ **sounddevice** - Audio input/output
- ✅ **OpenAI API Key** - For AI processing
- ✅ **Microphone** - For voice input
- ✅ **Speakers/Headphones** - For voice output

### Installation
```bash
# Install audio dependencies
pip install sounddevice

# Install OpenAI agents with voice support
pip install 'openai-agents[voice]'

# Set your OpenAI API key
$env:OPENAI_API_KEY="your-api-key-here"
```

## 🎯 Voice Commands

### Basic Commands
- **"hello"** - Get a greeting
- **"help"** - Show available commands
- **"quit"** - Exit the system

### Financial Research Commands
- **"analyze Apple"** - Research Apple Inc.
- **"analyze Tesla"** - Research Tesla Inc.
- **"report"** - Get latest financial report
- **"help"** - Show command list

## 🔧 How It Works

### 1. Voice Input (Speech-to-Text)
- Uses OpenAI's Whisper model for transcription
- Processes real-time audio from your microphone
- Converts speech to text commands

### 2. Command Processing
- Parses voice commands using AI
- Maps commands to financial research actions
- Provides conversational responses

### 3. Voice Output (Text-to-Speech)
- Converts AI responses to speech
- Uses OpenAI's TTS model
- Plays audio through your speakers

## 📁 File Structure

```
financial_research_agent/
├── voice_demo.py          # Simple voice demo
├── voice_main.py          # Full voice-enabled agent
├── voice_chat.py          # Voice workflow definitions
└── main.py               # Text-based version (fallback)
```

## 🎮 Usage Examples

### Example 1: Company Analysis
```
You: "Analyze Apple"
Agent: "Starting financial analysis of Apple. This will take a moment..."
[Agent performs research and generates report]
```

### Example 2: Get Help
```
You: "Help"
Agent: "Available voice commands:
- Say 'analyze [company name]' to research a company
- Say 'report' to get the latest financial report
- Say 'help' for this list
- Say 'quit' to exit"
```

### Example 3: Exit System
```
You: "Quit"
Agent: "Goodbye! Thank you for using the Financial Research Agent."
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "No module named 'agents.voice'"
**Solution**: Check that you're running from the correct directory
```bash
cd financial_agent
python financial_research_agent/voice_demo.py
```

#### 2. "OpenAI API quota exceeded"
**Solution**: Add payment method to your OpenAI account
- Visit: https://platform.openai.com/account/billing
- Add credit card or payment method

#### 3. "Microphone not working"
**Solution**: Check audio settings
- Ensure microphone is enabled
- Check Windows sound settings
- Test with other applications

#### 4. "No audio output"
**Solution**: Check speaker settings
- Ensure speakers/headphones are connected
- Check volume levels
- Test with other applications

### Fallback Options

If voice doesn't work, you can still use:
```bash
# Text-based version
python -m financial_research_agent.main

# Demo version
python demo_financial_agent.py
```

## 🔍 Advanced Configuration

### Custom Voice Workflow
Edit `voice_main.py` to customize:
- Voice commands
- Response styles
- Financial research parameters

### Audio Settings
Modify audio parameters in the voice components:
- Sample rate
- Audio format
- Buffer sizes

## 📚 Technical Details

### Voice Pipeline Components
1. **StreamedAudioInput** - Captures microphone audio
2. **VoicePipeline** - Orchestrates voice processing
3. **STT Model** - Speech-to-text conversion
4. **TTS Model** - Text-to-speech conversion
5. **Workflow** - Command processing logic

### Audio Specifications
- **Sample Rate**: 24kHz
- **Format**: 16-bit PCM
- **Channels**: Mono
- **Buffer Size**: 20ms chunks

## 🎉 Success Indicators

When voice is working correctly, you should see:
```
🎤 Voice-Enabled Financial Research Agent
========================================
🔍 Checking dependencies...
✅ sounddevice - Available
✅ Voice components - Available
✅ OpenAI API Key - Configured

🚀 All dependencies available! Starting voice system...
🎤 Starting voice pipeline...
💡 Speak clearly into your microphone
```

## 🆘 Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure your OpenAI API key is valid
4. Test with the simple voice demo first

## 🔮 Future Enhancements

Planned voice features:
- Multi-language support
- Custom voice commands
- Voice-based report navigation
- Real-time financial alerts
- Voice-controlled data visualization
