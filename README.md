# MeriTel - Online Meeting Transcription Platform

Transform your online meetings into searchable transcripts with AI-powered summaries, action items, and meeting outlines.

## Features

- **Platform Integration**: Import recordings from Zoom, Google Meet, or upload directly
- **Word-Level Timestamps**: Precise transcription with word-by-word timing
- **Speaker Diarization**: Automatic speaker identification and labeling
- **Synchronized Playback**: Audio player synced with transcript highlighting
- **AI-Powered Summaries**: 
  - Overview (2-3 paragraph summary)
  - Action Items (with assignees and deadlines)
  - Meeting Outline (topic-based breakdown)
- **Otter AI-like Interface**: Clean, intuitive UI with bottom audio player

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

4. Add your API keys to `.env`:
```
DEEPGRAM_API_KEY=your_deepgram_key
OPENAI_API_KEY=your_openai_key
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
```

5. Run the backend:
```bash
python app.py
```

Backend runs on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

Frontend runs on `http://localhost:3000`

## Usage

### Creating a Meeting

1. Open `http://localhost:3000`
2. Enter meeting title and description
3. Choose source:
   - **Upload Recording**: Select audio/video file from your computer
   - **Import from Zoom**: Connect your Zoom account and import
4. Click "Create Meeting"

### Viewing Transcripts

1. The meeting detail page opens automatically
2. Click "Transcribe Meeting" to generate transcript
3. Transcript appears with speaker labels and timestamps
4. Click any part of the transcript to jump to that point in the audio

### Generating Summaries

1. After transcription completes, click "Generate Summary"
2. View the structured summary with:
   - **Overview**: High-level meeting summary
   - **Action Items**: Checkable tasks with assignees
   - **Outline**: Topic-based breakdown with timestamps
3. Toggle between "Transcript" and "Summary" views

### Audio Playback

- Use the player at the bottom to play/pause
- Seek through the recording
- Current word in transcript is highlighted
- Click transcript segments to seek audio

## Architecture

### Backend (Python/Flask)

- `app.py`: Main Flask application with API endpoints
- `config.py`: Configuration management
- `storage.py`: File-based meeting/transcript/summary storage
- `word_timestamp_transcriber.py`: Deepgram/AssemblyAI integration
- `summarizer.py`: OpenAI/DeepSeek summary generation
- `platform_integrations/`: Zoom, Meet, Teams integration modules

### Frontend (React)

- `pages/CreateMeeting.js`: Meeting creation with file upload
- `pages/MeetingDetail.js`: Main meeting view (Otter AI-like)
- `components/AudioPlayer.js`: Synchronized audio player
- `components/SyncedTranscript.js`: Real-time transcript highlighting
- `components/StructuredSummary.js`: Three-section summary display
- `components/ActionItemsList.js`: Interactive action items
- `components/MeetingOutline.js`: Expandable meeting outline

## API Endpoints

### Meetings

- `POST /api/meetings` - Create new meeting
- `GET /api/meetings` - List all meetings
- `GET /api/meetings/{id}` - Get meeting details
- `PATCH /api/meetings/{id}` - Update meeting
- `DELETE /api/meetings/{id}` - Delete meeting

### Recording & Processing

- `POST /api/meetings/{id}/upload` - Upload audio/video file
- `POST /api/meetings/{id}/transcribe` - Transcribe recording
- `POST /api/meetings/{id}/summarize` - Generate summary
- `GET /api/meetings/{id}/audio` - Stream audio file

### Transcripts & Summaries

- `GET /api/meetings/{id}/transcript` - Get detailed transcript
- `GET /api/meetings/{id}/summary` - Get structured summary
- `PATCH /api/meetings/{id}/summary` - Update action items

### Platform Integration

- `GET /api/auth/zoom` - Initiate Zoom OAuth
- `GET /api/auth/zoom/callback` - Zoom OAuth callback
- `POST /api/meetings/import-zoom` - Import Zoom recording

## Technology Stack

**Backend:**
- Flask (Web framework)
- Deepgram/AssemblyAI (Transcription)
- OpenAI/DeepSeek (Summarization)
- Zoom SDK (Platform integration)

**Frontend:**
- React 18
- React Router 6
- Axios
- HTML5 Audio API

## Requirements

- Python 3.8+
- Node.js 16+
- API keys for:
  - Deepgram or AssemblyAI (transcription)
  - OpenAI or DeepSeek (summarization)
  - Zoom (optional, for Zoom integration)

## License

Private project

## Support

For issues or questions, please contact the development team.
