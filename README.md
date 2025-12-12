# MeriTel - Intelligent Voice Transcription & Meeting Summary System

**MeriTel** is an automated voice transcription and intelligent summary generation system for physical and virtual meetings. It addresses privacy concerns, provides word-by-word transcription, generates intelligent summaries, and includes speaker identification similar to Siri.

## ✨ Key Features

- **🎙️ Privacy-First Voice Recording**: Automatic consent management and privacy notices
- **✍️ Word-by-Word Transcription**: Real-time and post-meeting transcription with multiple service providers
- **🧠 Intelligent Summaries**: AI-powered summaries with key points and action items
- **👥 Speaker Identification**: 
  - Voice-based identification (like Siri/Otter) with voice sample training
  - Name-based identification
- **🔐 Privacy & Security**: End-to-end encryption, local storage options, secure cloud backup
- **📊 Meeting Analytics**: Speaking time, contribution analysis, participant metrics
- **📁 Export & Storage**: Download transcripts, summaries, and encrypted backups

## 🏗️ Architecture

### Backend (Python + Flask)
- `app.py` - Main Flask API server
- `config.py` - Configuration management
- `audio_recorder.py` - Audio recording functionality
- `transcriber.py` - Speech-to-text transcription
- `speaker_identification.py` - Speaker identification and diarization
- `summarizer.py` - Intelligent summary generation
- `storage.py` - Encrypted storage management

### Frontend (React)
- Modern, responsive UI
- Real-time recording interface
- Transcript and summary viewer
- Meeting management dashboard
- Settings and privacy controls

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip, npm

### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up API keys** (optional, for cloud services)
```
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
AZURE_SPEECH_KEY=your_azure_key
```

5. **Run the backend**
```bash
python app.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure API endpoint** (if backend is not on localhost:5000)
```bash
echo "REACT_APP_API_URL=http://your-backend-url:5000" > .env.local
```

3. **Run the frontend**
```bash
npm start
```

Frontend will be available at `http://localhost:3000`

## 📖 Usage Guide

### Creating a Meeting

1. Click "New Meeting" button
2. Enter meeting title and description
3. **Confirm recording consent** - System requires explicit consent
4. Select privacy mode (local, encrypted cloud, or standard cloud)
5. Click "Create Meeting"

### Recording a Meeting

1. Navigate to meeting details
2. Click "Start Recording" button
3. **System announces**: "Recording started - participants can confirm consent"
4. Participants identify themselves:
   - **Voice-based**: Say calibration sentences for voice recognition
   - **Name-based**: Enter their name when prompted
5. Click "Stop Recording" when done

### Speaker Identification

#### Voice-Based Identification (like Siri)
- System prompts: "Say this sentence: 'My name is [your name]'" or other calibration phrases
- Voice sample is recorded and stored locally
- System uses voice features (MFCC, spectral analysis) to identify speakers
- Requires 2+ samples per speaker for accuracy

#### Name-Based Identification
- Participants simply enter their name
- System tracks who spoke when based on timestamps
- No voice training required

### Transcription

1. After recording, click "Transcribe Meeting"
2. Choose transcription service:
   - Google Cloud Speech-to-Text (most accurate)
   - OpenAI Whisper (good balance)
   - Azure Speech Services
   - Local processing (fastest, less accurate)
3. System returns word-by-word transcript with timestamps

### Summary Generation

1. Click "Generate Summary"
2. Choose AI model:
   - OpenAI GPT (most intelligent)
   - HuggingFace BART (good quality)
   - Local model (fastest)
3. System generates:
   - Executive summary
   - Key points
   - Action items
   - Speaker contributions

## 🔐 Privacy & Security

### Data Encryption
- All meeting data encrypted with AES-256
- Encryption key stored locally (never sent to servers)
- Transcripts and summaries encrypted at rest

### Storage Options
- **Local Storage**: All data stays on your device
- **Encrypted Cloud**: Data encrypted before uploading
- **Standard Cloud**: Use with caution, data encrypted in transit

### Consent Management
- System requires explicit consent before recording
- Participants are informed recording is active
- Easy opt-out and data deletion options
- GDPR-compliant data retention policies

## 📊 API Endpoints

### Meetings
- `POST /api/meetings` - Create meeting
- `GET /api/meetings` - List all meetings
- `GET /api/meetings/<id>` - Get meeting details
- `DELETE /api/meetings/<id>/delete` - Delete meeting

### Recording
- `POST /api/meetings/<id>/start-recording` - Start recording
- `POST /api/meetings/<id>/stop-recording` - Stop recording
- `POST /api/meetings/<id>/upload-audio` - Upload audio file

### Transcription
- `POST /api/meetings/<id>/transcribe` - Transcribe meeting

### Speaker Identification
- `POST /api/meetings/<id>/register-participant` - Register speaker
- `POST /api/meetings/<id>/identify-speakers` - Identify speakers in recording
- `GET /api/speakers` - List all registered speakers

### Summary
- `POST /api/meetings/<id>/summarize` - Generate summary
- `GET /api/meetings/<id>/summary` - Get summary

### Export
- `GET /api/meetings/<id>/export?format=zip` - Export meeting data

## 🛠️ Configuration

Edit `backend/.env` to configure:

```env
FLASK_ENV=development
DEBUG=True

TRANSCRIPTION_SERVICE=google  # google, openai, azure, local
STT_MODEL=base
SPEAKER_DIARIZATION=true
SUMMARY_MODEL=openai  # openai, huggingface, local

PRIVACY_MODE=local  # local, encrypted_cloud, standard_cloud
STORAGE_TYPE=local  # local, aws, azure, google
ENCRYPTION_ENABLED=true

SAMPLE_RATE=16000
CHUNK_DURATION=1.0
```

## 📦 Dependencies

### Backend
- Flask 2.3.3 - Web framework
- librosa 0.10.0 - Audio processing
- transformers 4.31.0 - AI models
- cryptography 41.0.1 - Encryption
- numpy, scipy, soundfile - Audio utilities

### Frontend
- React 18.2.0 - UI framework
- axios 1.4.0 - HTTP client
- react-router-dom 6.14.0 - Routing

## 🐳 Docker Deployment

```bash
docker-compose up
```

Frontend: http://localhost:3000
Backend: http://localhost:5000

## 🤝 Contributing

This is an open-source project. Contributions are welcome!

## 📝 License

MIT License - See LICENSE file for details

## 🆘 Troubleshooting

### Audio not recording
- Check browser microphone permissions
- Ensure recording consent is confirmed
- Test microphone with browser's audio test

### Transcription errors
- Verify API keys are set correctly
- Check audio quality
- Try different transcription service

### Speaker identification not working
- Ensure clear voice samples during training
- Reduce noise in environment
- Try voice-based instead of name-based identification

## 📞 Support

For issues, questions, or suggestions, please create an issue on GitHub or contact support.

---

**MeriTel**: Making meetings more productive, transparent, and accessible. 🎙️✨
