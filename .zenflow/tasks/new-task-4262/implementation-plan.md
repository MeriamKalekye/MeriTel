# Implementation Plan: MeriTel Online Meeting Transformation

## Task Breakdown

### Task 1: Setup & Configuration
**Description**: Configure platform API credentials and update backend configuration

**Files to Modify**:
- `backend/config.py`
- `backend/.env.example` (create if not exists)

**Changes**:
```python
# Add to config.py
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
ZOOM_REDIRECT_URI = os.getenv('ZOOM_REDIRECT_URI', 'http://localhost:5000/api/auth/zoom/callback')

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')  # For word-level timestamps
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')  # Alternative
```

**Verification**:
- [ ] Environment variables load correctly
- [ ] Config values accessible in app.py

---

### Task 2: Backend Data Models Update
**Description**: Modify storage models for online meetings, timestamps, and structured summaries

**Files to Modify**:
- `backend/storage.py`

**Changes**:
1. Update meeting metadata schema to include:
   - `meeting_type`, `platform`, `platform_meeting_id`, `join_url`, `recording_url`, `duration`
   - Enhanced `participants` with `email`, `platform_user_id`, `avatar_url`

2. Create new `save_detailed_transcript()` method to store word-level timestamps:
   ```python
   def save_detailed_transcript(self, meeting_id, transcript_data):
       # Save JSON with segments and word-level timestamps
   ```

3. Create `save_structured_summary()` method for overview/action items/outline:
   ```python
   def save_structured_summary(self, meeting_id, summary_data):
       # Save structured summary with all sections
   ```

**Verification**:
- [ ] Create online meeting with new fields
- [ ] Save and retrieve detailed transcript
- [ ] Save and retrieve structured summary

---

### Task 3: Platform Integration Base
**Description**: Create abstract base class for platform integrations

**Files to Create**:
- `backend/platform_integrations/__init__.py`
- `backend/platform_integrations/base_platform.py`

**Implementation**:
```python
# base_platform.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BasePlatform(ABC):
    @abstractmethod
    def authenticate(self, code: str) -> Dict[str, Any]:
        """Complete OAuth flow and return access token"""
        pass
    
    @abstractmethod
    def get_meeting_details(self, meeting_id: str) -> Dict[str, Any]:
        """Get meeting metadata including participants"""
        pass
    
    @abstractmethod
    def download_recording(self, meeting_id: str, output_path: str) -> str:
        """Download meeting recording to local file"""
        pass
    
    @abstractmethod
    def get_participants(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get list of meeting participants"""
        pass
```

**Verification**:
- [ ] Base class imports successfully
- [ ] Abstract methods defined correctly

---

### Task 4: Zoom Integration
**Description**: Implement Zoom platform integration with OAuth and recording download

**Files to Create**:
- `backend/platform_integrations/zoom_integration.py`

**Files to Modify**:
- `backend/app.py` - Add OAuth routes

**Implementation**:

1. `zoom_integration.py`:
```python
class ZoomPlatform(BasePlatform):
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
    
    def authenticate(self, code):
        # Implement OAuth token exchange
        
    def get_meeting_details(self, meeting_id):
        # Call Zoom API: GET /meetings/{meetingId}
        
    def download_recording(self, meeting_id, output_path):
        # Call Zoom API: GET /meetings/{meetingId}/recordings
        # Download audio file
        
    def get_participants(self, meeting_id):
        # Call Zoom API: GET /past_meetings/{meetingId}/participants
```

2. Add to `app.py`:
```python
@app.route('/api/auth/zoom', methods=['GET'])
def zoom_auth():
    # Redirect to Zoom OAuth page
    
@app.route('/api/auth/zoom/callback', methods=['GET'])
def zoom_callback():
    # Handle OAuth callback, save token

@app.route('/api/meetings/import-zoom', methods=['POST'])
def import_zoom_meeting():
    # Import recording from Zoom
```

**Verification**:
- [ ] Zoom OAuth flow completes successfully
- [ ] Can fetch Zoom meeting details
- [ ] Can download Zoom recording
- [ ] Participant list extracted correctly

---

### Task 5: Enhanced Transcription with Timestamps
**Description**: Integrate Deepgram or AssemblyAI for word-level timestamp transcription

**Files to Modify**:
- `backend/transcriber.py`

**Files to Create**:
- `backend/word_timestamp_transcriber.py`

**Implementation**:

1. Create `word_timestamp_transcriber.py`:
```python
import requests
import json
from typing import Dict, Any

class WordTimestampTranscriber:
    def __init__(self, service='deepgram', api_key=None):
        self.service = service
        self.api_key = api_key
    
    def transcribe_with_timestamps(self, audio_path: str) -> Dict[str, Any]:
        if self.service == 'deepgram':
            return self._transcribe_deepgram(audio_path)
        elif self.service == 'assemblyai':
            return self._transcribe_assemblyai(audio_path)
    
    def _transcribe_deepgram(self, audio_path):
        # Use Deepgram API with diarization and word timestamps
        url = "https://api.deepgram.com/v1/listen"
        params = {
            'diarize': 'true',
            'punctuate': 'true',
            'utterances': 'true',
            'model': 'general',
        }
        # Implementation
    
    def _transcribe_assemblyai(self, audio_path):
        # Use AssemblyAI with speaker diarization
        # Implementation
```

2. Modify `transcriber.py` to use new class:
```python
def transcribe_file_with_timestamps(self, audio_path: str) -> Dict[str, Any]:
    if self.service in ['deepgram', 'assemblyai']:
        ts_transcriber = WordTimestampTranscriber(self.service, api_key)
        return ts_transcriber.transcribe_with_timestamps(audio_path)
    else:
        # Fallback to existing method
        return self.transcribe_file(audio_path)
```

**Verification**:
- [ ] Deepgram transcription returns word-level timestamps
- [ ] Speaker diarization identifies different speakers
- [ ] Timestamp accuracy within ±0.5s
- [ ] Handles 30+ minute recordings

---

### Task 6: Structured Summary Generation
**Description**: Enhance summarizer to generate Overview, Action Items, and Outline

**Files to Modify**:
- `backend/summarizer.py`
- `backend/app.py`

**Implementation**:

1. Add to `summarizer.py`:
```python
def generate_structured_summary_v2(self, transcript_segments: List[Dict], meeting_title: str) -> Dict[str, Any]:
    """Generate structured summary with Overview, Action Items, and Outline"""
    
    full_text = self._segments_to_text(transcript_segments)
    
    # Use GPT-3.5/GPT-4 with structured prompt
    prompt = f"""
    Analyze this meeting transcript and provide a structured summary:
    
    Meeting Title: {meeting_title}
    
    Transcript:
    {full_text}
    
    Please provide:
    1. OVERVIEW: A concise 2-3 paragraph summary of the meeting
    2. ACTION ITEMS: List of specific action items with format "- [Action] (Assignee: [Name], Due: [Date])"
    3. OUTLINE: Main topics discussed with timestamps
    
    Format your response as JSON.
    """
    
    # Call OpenAI/DeepSeek API
    # Parse JSON response
    # Return structured data
    
def extract_action_items_v2(self, text: str) -> List[Dict[str, Any]]:
    """Extract action items with assignees and deadlines"""
    # Use LLM to parse action items
    # Return list with {text, assignee, deadline, completed}
    
def generate_outline(self, transcript_segments: List[Dict]) -> List[Dict[str, Any]]:
    """Generate meeting outline with topics and timestamps"""
    # Use LLM to identify topic transitions
    # Return list with {topic, timestamp, duration, subtopics}
```

2. Add endpoint to `app.py`:
```python
@app.route('/api/meetings/<meeting_id>/summarize-structured', methods=['POST'])
def summarize_structured(meeting_id):
    # Load detailed transcript
    # Generate structured summary
    # Save and return
```

**Verification**:
- [ ] Overview is 2-3 coherent paragraphs
- [ ] At least 80% of action items extracted
- [ ] Outline has 3-5 logical topics
- [ ] JSON structure matches specification

---

### Task 7: Audio Player Component
**Description**: Create React audio player component with playback controls

**Files to Create**:
- `frontend/src/components/AudioPlayer.js`
- `frontend/src/components/AudioPlayer.css`
- `frontend/src/hooks/useAudioSync.js`

**Implementation**:

1. `useAudioSync.js` hook:
```javascript
import { useState, useEffect, useRef } from 'react';

export const useAudioSync = (audioRef) => {
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    
    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handleDurationChange = () => setDuration(audio.duration);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('durationchange', handleDurationChange);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    
    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('durationchange', handleDurationChange);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
    };
  }, [audioRef]);
  
  const seekTo = (time) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };
  
  return { currentTime, duration, isPlaying, seekTo };
};
```

2. `AudioPlayer.js`:
```javascript
import React, { useRef } from 'react';
import { useAudioSync } from '../hooks/useAudioSync';
import './AudioPlayer.css';

const AudioPlayer = ({ audioUrl, onTimeUpdate }) => {
  const audioRef = useRef(null);
  const { currentTime, duration, isPlaying, seekTo } = useAudioSync(audioRef);
  
  useEffect(() => {
    if (onTimeUpdate) {
      onTimeUpdate(currentTime);
    }
  }, [currentTime, onTimeUpdate]);
  
  const handlePlayPause = () => {
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
  };
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  return (
    <div className="audio-player">
      <audio ref={audioRef} src={audioUrl} />
      <button onClick={handlePlayPause}>
        {isPlaying ? '⏸' : '▶️'}
      </button>
      <div className="progress-bar">
        <input 
          type="range" 
          min="0" 
          max={duration} 
          value={currentTime}
          onChange={(e) => seekTo(parseFloat(e.target.value))}
        />
      </div>
      <span className="time-display">
        {formatTime(currentTime)} / {formatTime(duration)}
      </span>
    </div>
  );
};

export default AudioPlayer;
```

**Verification**:
- [ ] Audio plays/pauses correctly
- [ ] Progress bar shows accurate position
- [ ] Seeking works smoothly
- [ ] Time updates every 100ms

---

### Task 8: Synchronized Transcript Component
**Description**: Create transcript component with real-time highlighting and click-to-seek

**Files to Create**:
- `frontend/src/components/SyncedTranscript.js`
- `frontend/src/components/SyncedTranscript.css`
- `frontend/src/utils/transcriptHighlighter.js`

**Implementation**:

1. `transcriptHighlighter.js`:
```javascript
export const findCurrentSegment = (segments, currentTime) => {
  return segments.findIndex(seg => 
    currentTime >= seg.start_time && currentTime < seg.end_time
  );
};

export const findCurrentWord = (segment, currentTime) => {
  if (!segment || !segment.words) return -1;
  return segment.words.findIndex(word =>
    currentTime >= word.start && currentTime < word.end
  );
};
```

2. `SyncedTranscript.js`:
```javascript
import React, { useEffect, useRef } from 'react';
import { findCurrentSegment, findCurrentWord } from '../utils/transcriptHighlighter';
import './SyncedTranscript.css';

const SyncedTranscript = ({ segments, currentTime, onSeek }) => {
  const currentSegmentIndex = findCurrentSegment(segments, currentTime);
  const activeRef = useRef(null);
  
  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
    }
  }, [currentSegmentIndex]);
  
  return (
    <div className="synced-transcript">
      {segments.map((segment, index) => {
        const isActive = index === currentSegmentIndex;
        const currentWordIndex = isActive 
          ? findCurrentWord(segment, currentTime) 
          : -1;
        
        return (
          <div 
            key={segment.segment_id}
            className={`transcript-segment ${isActive ? 'active' : ''}`}
            ref={isActive ? activeRef : null}
            onClick={() => onSeek(segment.start_time)}
          >
            <div className="speaker-info">
              <span className="speaker-name">{segment.speaker_name}</span>
              <span className="timestamp">{formatTime(segment.start_time)}</span>
            </div>
            <div className="segment-text">
              {segment.words ? (
                segment.words.map((word, wIdx) => (
                  <span 
                    key={wIdx}
                    className={wIdx === currentWordIndex ? 'highlight-word' : ''}
                  >
                    {word.word}{' '}
                  </span>
                ))
              ) : (
                segment.text
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SyncedTranscript;
```

**Verification**:
- [ ] Current segment highlights correctly
- [ ] Current word highlights in real-time
- [ ] Auto-scrolls to keep active segment visible
- [ ] Clicking segment seeks audio correctly
- [ ] Performance smooth with 500+ segments

---

### Task 9: Structured Summary View
**Description**: Create summary component with Overview, Action Items, and Outline sections

**Files to Create**:
- `frontend/src/components/StructuredSummary.js`
- `frontend/src/components/ActionItemsList.js`
- `frontend/src/components/MeetingOutline.js`
- `frontend/src/components/StructuredSummary.css`

**Implementation**:

1. `ActionItemsList.js`:
```javascript
import React from 'react';

const ActionItemsList = ({ actionItems, onToggle, onSeek }) => {
  return (
    <div className="action-items-list">
      {actionItems.map(item => (
        <div key={item.id} className="action-item">
          <input 
            type="checkbox" 
            checked={item.completed}
            onChange={() => onToggle(item.id)}
          />
          <div className="action-content">
            <p>{item.text}</p>
            {item.assignee && <span className="assignee">@{item.assignee}</span>}
            {item.deadline && <span className="deadline">Due: {item.deadline}</span>}
          </div>
        </div>
      ))}
    </div>
  );
};
```

2. `MeetingOutline.js`:
```javascript
import React, { useState } from 'react';

const MeetingOutline = ({ outline, onSeek }) => {
  const [expanded, setExpanded] = useState({});
  
  const toggle = (topicId) => {
    setExpanded(prev => ({ ...prev, [topicId]: !prev[topicId] }));
  };
  
  return (
    <div className="meeting-outline">
      {outline.map((topic, idx) => (
        <div key={idx} className="outline-topic">
          <div 
            className="topic-header"
            onClick={() => {
              toggle(idx);
              onSeek(topic.timestamp);
            }}
          >
            <span className="expand-icon">{expanded[idx] ? '▼' : '▶'}</span>
            <span className="topic-title">{topic.topic}</span>
            <span className="topic-time">{formatDuration(topic.duration)}</span>
          </div>
          {expanded[idx] && topic.subtopics && (
            <ul className="subtopics">
              {topic.subtopics.map((sub, subIdx) => (
                <li key={subIdx}>{sub}</li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
};
```

3. `StructuredSummary.js`:
```javascript
import React from 'react';
import ActionItemsList from './ActionItemsList';
import MeetingOutline from './MeetingOutline';
import './StructuredSummary.css';

const StructuredSummary = ({ summary, onSeek, onToggleActionItem }) => {
  return (
    <div className="structured-summary">
      <section className="summary-section">
        <h3>📝 Overview</h3>
        <div className="overview-text">
          {summary.overview.text}
        </div>
      </section>
      
      <section className="summary-section">
        <h3>✅ Action Items</h3>
        <ActionItemsList 
          actionItems={summary.action_items}
          onToggle={onToggleActionItem}
        />
      </section>
      
      <section className="summary-section">
        <h3>📋 Outline</h3>
        <MeetingOutline 
          outline={summary.outline}
          onSeek={onSeek}
        />
      </section>
    </div>
  );
};

export default StructuredSummary;
```

**Verification**:
- [ ] Three sections display correctly
- [ ] Action items are toggleable
- [ ] Outline topics are expandable
- [ ] Clicking outline seeks to timestamp
- [ ] Mobile responsive design

---

### Task 10: Update Meeting Creation Flow
**Description**: Add platform selection and file upload to meeting creation

**Files to Modify**:
- `frontend/src/pages/CreateMeeting.js`
- `frontend/src/pages/CreateMeeting.css`

**Implementation**:

Add platform selection and upload:
```javascript
const [meetingType, setMeetingType] = useState('upload'); // 'zoom', 'meet', 'upload'
const [uploadedFile, setUploadedFile] = useState(null);
const [zoomMeetingId, setZoomMeetingId] = useState('');

const handleFileUpload = (e) => {
  setUploadedFile(e.target.files[0]);
};

const handleCreateMeeting = async (e) => {
  e.preventDefault();
  
  if (meetingType === 'upload' && uploadedFile) {
    // Upload file and create meeting
    const formData = new FormData();
    formData.append('audio', uploadedFile);
    formData.append('title', formData.title);
    formData.append('description', formData.description);
    
    const response = await axios.post(
      `${API_BASE_URL}/api/meetings/upload-recording`,
      formData
    );
  } else if (meetingType === 'zoom') {
    // Import from Zoom
    const response = await axios.post(
      `${API_BASE_URL}/api/meetings/import-zoom`,
      { zoom_meeting_id: zoomMeetingId, ...formData }
    );
  }
};
```

Add UI:
```jsx
<div className="form-group">
  <label>Meeting Source</label>
  <select value={meetingType} onChange={(e) => setMeetingType(e.target.value)}>
    <option value="upload">Upload Recording</option>
    <option value="zoom">Import from Zoom</option>
    <option value="meet">Import from Google Meet</option>
  </select>
</div>

{meetingType === 'upload' && (
  <div className="form-group">
    <label>Audio/Video File</label>
    <input type="file" accept="audio/*,video/*" onChange={handleFileUpload} />
  </div>
)}

{meetingType === 'zoom' && (
  <div className="form-group">
    <label>Zoom Meeting ID</label>
    <input 
      type="text" 
      value={zoomMeetingId}
      onChange={(e) => setZoomMeetingId(e.target.value)}
      placeholder="Enter Zoom meeting ID"
    />
    <button onClick={handleConnectZoom}>Connect to Zoom</button>
  </div>
)}
```

**Verification**:
- [ ] Can upload audio file (MP3, WAV, M4A)
- [ ] Can upload video file (MP4, MOV)
- [ ] File size validation (max 500MB)
- [ ] Zoom connection flow works

---

### Task 11: Meeting Detail Redesign
**Description**: Complete overhaul of MeetingDetail page with audio player, synced transcript, and structured summary

**Files to Modify**:
- `frontend/src/pages/MeetingDetail.js`
- `frontend/src/pages/MeetingDetail.css`

**Implementation**:

Replace entire component structure:
```javascript
const MeetingDetail = ({ meetingId }) => {
  const [meeting, setMeeting] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [summary, setSummary] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [view, setView] = useState('transcript'); // 'transcript' or 'summary'
  
  const handleSeek = (time) => {
    setCurrentTime(time);
    // Trigger audio player seek
  };
  
  return (
    <div className="meeting-detail-v2">
      <header className="meeting-header">
        <h1>{meeting.title}</h1>
        <div className="meeting-meta">
          <span>📅 {formatDate(meeting.created_at)}</span>
          <span>👥 {meeting.participants.length} participants</span>
          <span>⏱ {formatDuration(meeting.duration)}</span>
        </div>
      </header>
      
      <div className="content-area">
        <div className="view-toggle">
          <button 
            className={view === 'transcript' ? 'active' : ''}
            onClick={() => setView('transcript')}
          >
            Transcript
          </button>
          <button 
            className={view === 'summary' ? 'active' : ''}
            onClick={() => setView('summary')}
          >
            Summary
          </button>
        </div>
        
        <div className="main-content">
          {view === 'transcript' ? (
            <SyncedTranscript 
              segments={transcript.segments}
              currentTime={currentTime}
              onSeek={handleSeek}
            />
          ) : (
            <StructuredSummary 
              summary={summary}
              onSeek={handleSeek}
            />
          )}
        </div>
      </div>
      
      <footer className="audio-player-footer">
        <AudioPlayer 
          audioUrl={meeting.recording_url}
          onTimeUpdate={setCurrentTime}
        />
      </footer>
    </div>
  );
};
```

Add CSS for Otter AI-like layout:
```css
.meeting-detail-v2 {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.content-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.audio-player-footer {
  position: sticky;
  bottom: 0;
  background: white;
  border-top: 1px solid #ddd;
  padding: 16px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}
```

**Verification**:
- [ ] Layout matches Otter AI reference images
- [ ] Audio player stays at bottom
- [ ] Transcript scrolls independently
- [ ] View toggle works smoothly
- [ ] Responsive on mobile

---

### Task 12: Testing & Refinement
**Description**: End-to-end testing, bug fixes, and polish

**Test Scenarios**:

1. **Upload Flow**:
   - [ ] Upload 5-minute audio file
   - [ ] Transcription completes
   - [ ] Summary generates
   - [ ] Audio plays with sync
   
2. **Zoom Flow**:
   - [ ] Connect Zoom account
   - [ ] Import meeting
   - [ ] Participants load correctly
   - [ ] Recording downloads
   
3. **Playback & Sync**:
   - [ ] Play/pause works
   - [ ] Seeking updates transcript
   - [ ] Clicking transcript seeks audio
   - [ ] Word highlighting accurate
   - [ ] Auto-scroll smooth
   
4. **Summary**:
   - [ ] Overview is coherent
   - [ ] Action items have assignees
   - [ ] Outline has 3+ topics
   - [ ] Clicking outline seeks audio
   
5. **Performance**:
   - [ ] 1-hour meeting loads in <3s
   - [ ] Smooth scrolling with 1000+ segments
   - [ ] No memory leaks
   - [ ] Mobile performance acceptable
   
6. **Edge Cases**:
   - [ ] No speaker diarization
   - [ ] Very short meeting (<1 min)
   - [ ] Very long meeting (>2 hours)
   - [ ] Poor audio quality
   - [ ] Network interruption during upload

**Bug Fixes & Polish**:
- Fix any visual glitches
- Improve error messages
- Add loading states
- Add empty states
- Improve accessibility (ARIA labels, keyboard navigation)
- Add export functionality (PDF, DOCX)

**Verification**:
- [ ] All test scenarios pass
- [ ] No console errors
- [ ] Lighthouse score >80
- [ ] Works in Chrome, Firefox, Safari
- [ ] Mobile responsive
