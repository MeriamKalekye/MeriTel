# Technical Specification: Transform MeriTel to Online Meeting Platform

## Difficulty Assessment
**Complexity**: Hard

This is a complex transformation requiring:
- Major architectural changes from physical to online meeting paradigm
- Real-time synchronized audio player with transcript highlighting
- Time-aligned transcription with word-level timestamps
- Structured summary generation (Overview, Action Items, Outline)
- Integration with online meeting platforms or custom WebRTC solution
- Speaker diarization improvements
- Complex UI/UX overhaul

## Technical Context

### Current Stack
- **Backend**: Python 3.x, Flask, Flask-CORS
- **Frontend**: React 18.2.0, React Router 6.14.0, Axios 1.4.0
- **Audio Processing**: librosa, soundfile, numpy
- **Transcription**: Multiple services (Google Cloud Speech, OpenAI Whisper, local models)
- **Summarization**: OpenAI GPT-3.5, DeepSeek, Hugging Face BART models
- **Speaker ID**: MFCC-based voice features with librosa

### Current Dependencies (Backend)
- Flask, Flask-CORS
- librosa, soundfile, numpy
- Google Cloud Speech API (optional)
- OpenAI API (optional)
- transformers (for local models)

### Current Dependencies (Frontend)
- react, react-dom, react-router-dom
- axios
- recharts, react-icons
- @emotion/react, @emotion/styled

## Implementation Approach

### 1. Online Meeting Integration Strategy

#### Option A: Platform Integration (Recommended)
Integrate with existing platforms via their APIs:
- **Zoom**: Use Zoom SDK/API for bot-based recording
- **Google Meet**: Use Meet API for recording access
- **Microsoft Teams**: Use Graph API for meeting recordings

#### Option B: Custom WebRTC Solution
Build custom online meeting infrastructure:
- Use WebRTC for peer-to-peer audio/video
- Implement server-side recording with MediaRecorder API
- More control but significantly more complexity

**Decision**: Start with Option A (Zoom integration) as it provides better speaker identification and is closer to Otter AI's approach.

### 2. Core Architecture Changes

#### Backend Changes
1. **New Meeting Types**
   - Add `meeting_type` field: `online` or `physical`
   - Online meetings require platform credentials (Zoom, Meet, etc.)
   - Store meeting platform metadata (meeting_id, join_url, etc.)

2. **Online Meeting Recording Flow**
   - Replace physical microphone recording with platform recording download
   - Use platform APIs to fetch recordings after meeting ends
   - Leverage platform's speaker identification (participants list)

3. **Enhanced Transcription with Timestamps**
   - Modify transcriber to capture word-level timestamps
   - Store transcript as structured JSON with:
     ```json
     {
       "segments": [
         {
           "speaker_id": "participant_123",
           "speaker_name": "John Doe",
           "start_time": 0.5,
           "end_time": 3.2,
           "text": "Hello everyone",
           "words": [
             {"word": "Hello", "start": 0.5, "end": 0.9},
             {"word": "everyone", "start": 1.0, "end": 1.5}
           ]
         }
       ]
     }
     ```
   - Use services that support word-level timestamps (Deepgram, AssemblyAI, OpenAI Whisper API)

4. **Structured Summary Generation**
   - Enhance summarizer to generate three distinct sections:
     - **Overview**: High-level summary (2-3 paragraphs)
     - **Action Items**: Extracted tasks with assignees and deadlines
     - **Outline**: Topic-based breakdown of discussion
   - Use prompt engineering with GPT-3.5/GPT-4 or DeepSeek for structured output

5. **Speaker Diarization**
   - Leverage online platform's participant list for speaker names
   - Map platform participant IDs to transcript segments
   - Fallback to acoustic diarization for unmapped segments

#### Frontend Changes
1. **Audio Player Component**
   - Create new `AudioPlayer.js` component with:
     - HTML5 audio element
     - Custom playback controls (play/pause, seek, speed)
     - Progress bar synchronized with transcript
     - Current time display

2. **Synchronized Transcript View**
   - Create `SyncedTranscript.js` component
   - Highlight current segment/word based on audio playback time
   - Click on transcript segment to jump to that time in audio
   - Auto-scroll to keep current segment visible
   - Display speaker avatars/names with color coding

3. **Summary View Redesign**
   - Restructure summary tab to show three sections:
     - **Overview** section at top
     - **Action Items** as checkable list with metadata
     - **Outline** as expandable/collapsible tree structure
   - Add template selector (General, Sales, Engineering, etc.)

4. **Meeting Creation Flow**
   - Add platform selection (Zoom, Meet, Custom Upload)
   - For platform meetings: OAuth flow for authorization
   - For custom upload: Direct audio/video file upload
   - Remove physical recording consent flow (not needed for online)

5. **Meeting Detail View**
   - Replace recording interface with:
     - Audio player at bottom (like Otter AI)
     - Transcript in center with real-time highlighting
     - Summary/Outline toggle on right sidebar
   - Add export options (PDF, DOCX, TXT)

### 3. Data Model Changes

#### Meeting Model
```python
{
  'meeting_id': str,
  'title': str,
  'description': str,
  'meeting_type': 'online' | 'physical',  # NEW
  'platform': 'zoom' | 'meet' | 'teams' | 'upload',  # NEW
  'platform_meeting_id': str,  # NEW
  'join_url': str,  # NEW
  'recording_url': str,  # MODIFIED (was recording_path)
  'audio_file_path': str,  # NEW (local copy)
  'duration': int,  # NEW (in seconds)
  'status': 'created' | 'scheduled' | 'in_progress' | 'recorded' | 'transcribed' | 'completed',
  'participants': [
    {
      'id': str,
      'name': str,
      'email': str,  # NEW
      'platform_user_id': str,  # NEW
      'avatar_url': str,  # NEW
    }
  ],
  'created_at': datetime,
  'started_at': datetime,
  'ended_at': datetime
}
```

#### Transcript Model
```python
{
  'meeting_id': str,
  'segments': [
    {
      'segment_id': str,
      'speaker_id': str,
      'speaker_name': str,
      'start_time': float,
      'end_time': float,
      'text': str,
      'confidence': float,
      'words': [
        {
          'word': str,
          'start': float,
          'end': float,
          'confidence': float
        }
      ]
    }
  ],
  'created_at': datetime,
  'service': str
}
```

#### Summary Model
```python
{
  'meeting_id': str,
  'overview': {
    'text': str,
    'word_count': int
  },
  'action_items': [
    {
      'id': str,
      'text': str,
      'assignee': str,
      'deadline': str,
      'completed': bool
    }
  ],
  'outline': [
    {
      'topic': str,
      'timestamp': float,
      'subtopics': [str],
      'duration': float
    }
  ],
  'keywords': [str],
  'sentiment': str,  # positive, neutral, negative
  'created_at': datetime,
  'template': str
}
```

### 4. API Changes

#### New Endpoints
```
POST   /api/meetings/connect-platform       # OAuth flow for Zoom/Meet
POST   /api/meetings/upload-recording       # Direct file upload
GET    /api/meetings/<id>/recording         # Serve audio file
GET    /api/meetings/<id>/transcript        # Get detailed transcript with timestamps
GET    /api/meetings/<id>/summary           # Get structured summary
PATCH  /api/meetings/<id>/action-items/<id> # Update action item status
```

#### Modified Endpoints
```
POST   /api/meetings                        # Add platform metadata
GET    /api/meetings/<id>                   # Return full model
POST   /api/meetings/<id>/transcribe        # Use timestamp-aware transcription
POST   /api/meetings/<id>/summarize         # Generate structured summary
```

#### Deprecated Endpoints
```
POST   /api/meetings/<id>/start-recording   # Not needed for online meetings
POST   /api/meetings/<id>/stop-recording    # Not needed for online meetings
POST   /api/meetings/<id>/register-participant # Use platform participant data
```

## Source Code Structure Changes

### Backend Files to Create
1. `backend/platform_integrations/zoom_integration.py` - Zoom SDK wrapper
2. `backend/platform_integrations/meet_integration.py` - Google Meet integration
3. `backend/platform_integrations/base_platform.py` - Abstract base class
4. `backend/diarization.py` - Enhanced speaker diarization
5. `backend/word_timestamp_transcriber.py` - Word-level timestamp extraction

### Backend Files to Modify
1. `backend/app.py` - Add new endpoints, modify existing ones
2. `backend/transcriber.py` - Add word-level timestamp support
3. `backend/summarizer.py` - Add structured summary generation
4. `backend/speaker_identification.py` - Integrate with platform participant data
5. `backend/storage.py` - Handle new data models
6. `backend/config.py` - Add platform API keys and configuration

### Backend Files to Remove/Deprecate
1. `backend/audio_recorder.py` - No longer needed for online meetings

### Frontend Files to Create
1. `frontend/src/components/AudioPlayer.js` - Audio playback component
2. `frontend/src/components/SyncedTranscript.js` - Synchronized transcript view
3. `frontend/src/components/StructuredSummary.js` - Three-section summary display
4. `frontend/src/components/PlatformConnector.js` - OAuth/platform connection
5. `frontend/src/components/ActionItemsList.js` - Interactive action items
6. `frontend/src/components/MeetingOutline.js` - Outline tree view
7. `frontend/src/hooks/useAudioSync.js` - Custom hook for audio-transcript sync
8. `frontend/src/utils/transcriptHighlighter.js` - Highlight current words/segments

### Frontend Files to Modify
1. `frontend/src/pages/MeetingDetail.js` - Complete redesign with new components
2. `frontend/src/pages/CreateMeeting.js` - Add platform selection and upload
3. `frontend/src/pages/MeetingsList.js` - Display platform badges
4. `frontend/src/App.js` - Add platform auth routes
5. `frontend/src/App.css` - New styling for audio player and synced view

### Frontend Files to Remove/Deprecate
1. Consent flow components (embedded in MeetingDetail.js) - Not needed

## Verification Approach

### Phase 1: Platform Integration
- [ ] Successfully connect to Zoom API with OAuth
- [ ] Download sample meeting recording from Zoom
- [ ] Extract participant list from Zoom meeting

### Phase 2: Enhanced Transcription
- [ ] Transcribe recording with word-level timestamps
- [ ] Verify timestamp accuracy (±0.5s tolerance)
- [ ] Map speakers to transcript segments with >90% accuracy

### Phase 3: Audio Player & Sync
- [ ] Audio plays correctly in browser
- [ ] Transcript highlights current segment during playback
- [ ] Clicking transcript seeks to correct audio position
- [ ] Performance smooth with 1-hour meeting

### Phase 4: Structured Summary
- [ ] Generate overview (2-3 paragraphs)
- [ ] Extract at least 80% of action items
- [ ] Create logical outline with 3-5 main topics

### Phase 5: End-to-End Testing
- [ ] Create online meeting via Zoom
- [ ] Upload recording automatically
- [ ] View synchronized transcript
- [ ] Review structured summary
- [ ] Export to PDF/DOCX

## Dependencies to Add

### Backend
```
deepgram-sdk==2.10.0          # For word-level timestamps
zoom-sdk==1.0.0               # Zoom integration (if available)
google-meet-api==1.0.0        # Google Meet integration
assemblyai==0.17.0            # Alternative transcription with timestamps
python-docx==0.8.11           # For DOCX export
reportlab==4.0.7              # For PDF export
```

### Frontend
```
wavesurfer.js==7.0.0          # Audio waveform visualization (optional)
react-h5-audio-player==3.9.0  # Pre-built audio player (alternative)
```

## Risk Considerations

1. **Platform API Rate Limits**: Zoom/Meet APIs have rate limits
   - Mitigation: Implement queueing and retry logic

2. **Transcription Accuracy**: Word timestamps may be inaccurate
   - Mitigation: Use high-quality services (Deepgram, AssemblyAI)

3. **Large File Handling**: 2-hour meetings = large audio files
   - Mitigation: Stream audio, paginate transcript

4. **Speaker Diarization Errors**: Platform data may not match audio
   - Mitigation: Hybrid approach with acoustic diarization fallback

## Migration Strategy

1. **Backward Compatibility**: Keep physical meeting support
   - Add `meeting_type` field with default `physical`
   - Keep old recording flow for physical meetings
   - New UI adapts based on meeting type

2. **Gradual Rollout**: 
   - Phase 1: Add upload functionality
   - Phase 2: Add Zoom integration
   - Phase 3: Add structured summary
   - Phase 4: Add other platforms

3. **Data Migration**: Existing meetings remain functional
   - Add `meeting_type='physical'` to all existing meetings
   - Old transcript format converts to new format on demand

## Implementation Plan

The implementation will be broken down into 12 concrete tasks in `plan.md`:

1. **Setup & Configuration**: Add platform API keys, update config
2. **Backend Data Models**: Modify meeting/transcript/summary models
3. **Platform Integration Base**: Create base platform class
4. **Zoom Integration**: Implement Zoom OAuth and recording download
5. **Enhanced Transcription**: Add word-level timestamp support
6. **Structured Summarization**: Generate Overview, Action Items, Outline
7. **Audio Player Component**: Build synchronized audio player
8. **Synced Transcript Component**: Real-time highlighting and seeking
9. **Summary View Redesign**: Three-section summary display
10. **Meeting Creation Update**: Platform selection and upload
11. **Meeting Detail Redesign**: Complete UI overhaul
12. **Testing & Refinement**: End-to-end testing and polish

Each task will be detailed in the implementation plan with specific files, functions, and verification steps.
