# MeriTel - AI-Powered Meeting Bot Platform

An Otter.ai-like meeting bot that joins Google Meet/Zoom meetings, records conversations, generates AI transcripts with speaker diarization, and creates structured summaries.

## Features

- 🤖 **Live Meeting Bot**: Automated bot joins Google Meet/Zoom as a participant
- 🎙️ **Real-time Recording**: Captures meeting audio automatically
- 📝 **AI Transcription**: Word-level timestamps and speaker diarization (AssemblyAI/Deepgram)
- 🧠 **Smart Summaries**: AI-generated meeting summaries with:
  - Overview
  - Action Items
  - Structured Outline
- 🎯 **Multi-platform**: Supports Google Meet, Zoom, Microsoft Teams
- 📊 **Meeting Dashboard**: View all recordings, transcripts, and summaries

## Tech Stack

### Backend
- **Flask** - REST API server
- **Flask-SocketIO** - Real-time WebSocket communication
- **Playwright** - Browser automation for bot joining
- **AssemblyAI** - Speech-to-text with speaker diarization
- **DeepSeek** - AI-powered meeting summarization
- **Pydub + Noisereduce** - Audio processing and echo reduction

### Frontend
- **React** - User interface
- **React Router** - Navigation
- **Axios** - API communication
- **Socket.io-client** - Real-time updates

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- FFmpeg (for audio processing)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
playwright install chromium

# Configure API keys
cp .env.example .env
# Edit .env with your API keys:
# - ASSEMBLYAI_API_KEY
# - DEEPSEEK_API_KEY

python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Configuration

Edit `backend/.env`:

```env
ASSEMBLYAI_API_KEY=your_assemblyai_key
DEEPSEEK_API_KEY=your_deepseek_key
DEFAULT_TRANSCRIPTION_SERVICE=assemblyai
DEFAULT_SUMMARIZATION_SERVICE=deepseek
```

## Usage

1. **Start a Meeting Bot**:
   - Click "Join Live Meeting"
   - Enter meeting URL (Google Meet/Zoom)
   - Bot joins automatically and starts recording

2. **Stop Recording**:
   - Click "Stop Recording" when meeting ends
   - Audio is saved and ready for transcription

3. **Transcribe**:
   - Click "Transcribe Meeting"
   - Wait for AI transcription with speaker labels

4. **Generate Summary**:
   - Click "Generate Summary"
   - AI creates structured meeting notes

## API Keys

Get your API keys:
- **AssemblyAI**: https://www.assemblyai.com/
- **DeepSeek**: https://platform.deepseek.com/

## Known Limitations

- Browser automation has echo issues (bot hears itself)
- Speaker identification based on voice patterns, not names
- Requires FFmpeg for audio processing
- Google Meet may require user approval for bot to join

## Future Enhancements

- Google Meet API integration (requires Workspace)
- Zoom Cloud Recording API
- Advanced echo cancellation
- Calendar integration
- Real-time transcription during meetings
- Custom vocabulary for better accuracy

## License

MIT

## Contributing

Pull requests welcome!
