# MeriTel - AI-Powered Meeting Intelligence Platform

A comprehensive meeting assistant that records, transcribes, and summarizes both physical and online meetings with AI-powered speaker diarization and structured summaries.

## Features

### 🔊 Physical Meetings
- 🎙️ **Browser Recording**: Record meetings directly from your microphone
- 📤 **File Upload**: Upload pre-recorded meetings (MP3, WAV, MP4, M4A)
- 💾 **Drag & Drop**: Easy file upload interface (up to 500MB)

### 🌐 Online Meetings
- 🤖 **Automated Bot**: Bot joins Google Meet/Zoom as a participant
- 🎬 **Live Recording**: Captures meeting audio automatically
- 🎯 **Multi-platform**: Google Meet, Zoom, Microsoft Teams

### 🧠 AI-Powered Intelligence
- 📝 **Smart Transcription**: Word-level timestamps with speaker diarization (AssemblyAI/Deepgram)
- 👥 **Speaker Detection**: Automatic participant identification
- 📊 **Structured Summaries**: AI-generated meeting notes with:
  - Overview
  - Action Items
  - Structured Outline
- 🔄 **Re-transcribe & Re-generate**: Update transcripts and summaries anytime
- 📊 **Unified Dashboard**: Manage all physical and online meetings in one place

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

### Physical Meetings

1. **Record Now**:
   - Click "Physical Meeting" → "Record Now"
   - Enter meeting title and description
   - Click "Start Recording" (grant microphone access)
   - Pause/Resume as needed
   - Click "Stop & Save" when done

2. **Upload Recording**:
   - Click "Physical Meeting" → "Upload Recording"
   - Enter meeting title and description
   - Drag & drop or select audio file (MP3, WAV, MP4, M4A)
   - Upload and process

### Online Meetings

1. **Start Meeting Bot**:
   - Click "Online Meeting"
   - Enter meeting URL (Google Meet/Zoom)
   - Bot joins automatically and starts recording

2. **Stop Recording**:
   - Click "Stop Recording" when meeting ends
   - Audio is saved and ready for transcription

### Processing

3. **Transcribe**:
   - Open any meeting from your dashboard
   - Click "📝 Transcribe Meeting"
   - AI generates transcript with speaker labels

4. **Generate Summary**:
   - Click "🧠 Generate Summary"
   - AI creates structured meeting notes with action items

5. **Re-process**:
   - Click "🔄 Re-transcribe" or "🔄 Re-generate" to update existing content

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
