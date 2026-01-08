import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import AudioPlayer from '../components/AudioPlayer';
import SyncedTranscript from '../components/SyncedTranscript';
import StructuredSummary from '../components/StructuredSummary';
import { formatTime, formatDuration } from '../utils/transcriptHighlighter';
import './MeetingDetail.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const MeetingDetail = () => {
  const { meetingId } = useParams();
  const navigate = useNavigate();
  const audioPlayerRef = useRef(null);
  
  const [meeting, setMeeting] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [summary, setSummary] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [view, setView] = useState('transcript');
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadMeetingData();
  }, [meetingId]);

  const loadMeetingData = async () => {
    try {
      setIsLoading(true);
      setError('');

      const meetingResponse = await axios.get(`${API_BASE_URL}/api/meetings/${meetingId}`);
      setMeeting(meetingResponse.data.meeting);

      try {
        const transcriptResponse = await axios.get(`${API_BASE_URL}/api/meetings/${meetingId}/transcript`);
        setTranscript(transcriptResponse.data.transcript);
      } catch (err) {
        console.log('No transcript available yet');
      }

      try {
        const summaryResponse = await axios.get(`${API_BASE_URL}/api/meetings/${meetingId}/summary`);
        setSummary(summaryResponse.data.summary);
      } catch (err) {
        console.log('No summary available yet');
      }
    } catch (err) {
      console.error('Error loading meeting:', err);
      setError('Failed to load meeting');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTranscribe = async () => {
    try {
      setIsProcessing(true);
      setError('');

      const response = await axios.post(
        `${API_BASE_URL}/api/meetings/${meetingId}/transcribe`,
        {},
        { headers: { 'Content-Type': 'application/json' } }
      );
      setTranscript(response.data.transcript);
      await loadMeetingData();
    } catch (err) {
      console.error('Error transcribing:', err);
      setError(err.response?.data?.error || 'Failed to transcribe meeting');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleGenerateSummary = async () => {
    try {
      setIsProcessing(true);
      setError('');

      const response = await axios.post(
        `${API_BASE_URL}/api/meetings/${meetingId}/summarize`,
        {},
        { headers: { 'Content-Type': 'application/json' } }
      );
      setSummary(response.data.summary);
    } catch (err) {
      console.error('Error generating summary:', err);
      setError(err.response?.data?.error || 'Failed to generate summary');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSeek = (time) => {
    setCurrentTime(time);
  };

  const handleToggleActionItem = async (itemId) => {
    if (!summary || !summary.action_items) return;

    const updatedItems = summary.action_items.map(item => {
      if ((item.id || summary.action_items.indexOf(item)) === itemId) {
        return { ...item, completed: !item.completed };
      }
      return item;
    });

    setSummary({ ...summary, action_items: updatedItems });

    try {
      await axios.patch(`${API_BASE_URL}/api/meetings/${meetingId}/summary`, {
        action_items: updatedItems
      });
    } catch (err) {
      console.error('Error updating action item:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="meeting-detail-loading">
        <div className="loading-spinner"></div>
        <p>Loading meeting...</p>
      </div>
    );
  }

  if (error && !meeting) {
    return (
      <div className="meeting-detail-error">
        <p>{error}</p>
        <button onClick={() => navigate('/')}>Go Back</button>
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="meeting-detail-error">
        <p>Meeting not found</p>
        <button onClick={() => navigate('/')}>Go Back</button>
      </div>
    );
  }

  const hasRecording = meeting.audio_file_path || meeting.recording_url;
  const hasTranscript = transcript && transcript.segments && transcript.segments.length > 0;
  const hasSummary = summary && (summary.overview || summary.action_items || summary.outline);

  return (
    <div className="meeting-detail-v2">
      <header className="meeting-header">
        <button className="back-button" onClick={() => navigate('/')}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back
        </button>
        
        <div className="meeting-title-section">
          <h1>{meeting.title}</h1>
          {meeting.description && <p className="meeting-description">{meeting.description}</p>}
        </div>
        
        <div className="meeting-meta">
          <span className="meta-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="2" y="3" width="12" height="11" rx="2" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M5 1v3M11 1v3M2 6h12" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            {new Date(meeting.created_at).toLocaleDateString()}
          </span>
          <span className="meta-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="6" r="3" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M2 14c0-3 2.5-5 6-5s6 2 6 5" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            {meeting.participants?.length || 0} participants
          </span>
          {meeting.duration > 0 && (
            <span className="meta-item">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M8 4v4l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              {formatDuration(meeting.duration)}
            </span>
          )}
        </div>

        {!hasTranscript && hasRecording && (
          <button 
            className="action-button primary"
            onClick={handleTranscribe}
            disabled={isProcessing}
          >
            {isProcessing ? 'Transcribing...' : '📝 Transcribe Meeting'}
          </button>
        )}

        {hasTranscript && !hasSummary && (
          <button 
            className="action-button primary"
            onClick={handleGenerateSummary}
            disabled={isProcessing}
          >
            {isProcessing ? 'Generating...' : '🧠 Generate Summary'}
          </button>
        )}
      </header>

      <div className="content-area">
        <div className="view-toggle">
          <button 
            className={`toggle-button ${view === 'transcript' ? 'active' : ''}`}
            onClick={() => setView('transcript')}
          >
            Transcript
          </button>
          <button 
            className={`toggle-button ${view === 'summary' ? 'active' : ''}`}
            onClick={() => setView('summary')}
            disabled={!hasSummary}
          >
            Summary
          </button>
        </div>

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        <div className="main-content">
          {view === 'transcript' ? (
            hasTranscript ? (
              <SyncedTranscript 
                segments={transcript.segments}
                currentTime={currentTime}
                onSeek={handleSeek}
              />
            ) : (
              <div className="content-placeholder">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <rect x="12" y="16" width="40" height="32" rx="2" stroke="#ccc" strokeWidth="2"/>
                  <path d="M20 26h24M20 32h24M20 38h16" stroke="#ccc" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                <p>No transcript available yet</p>
                {hasRecording && (
                  <button className="placeholder-action" onClick={handleTranscribe}>
                    Transcribe Recording
                  </button>
                )}
              </div>
            )
          ) : (
            hasSummary ? (
              <StructuredSummary 
                summary={summary}
                onSeek={handleSeek}
                onToggleActionItem={handleToggleActionItem}
              />
            ) : (
              <div className="content-placeholder">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <circle cx="32" cy="32" r="20" stroke="#ccc" strokeWidth="2"/>
                  <path d="M32 22v10l6 6" stroke="#ccc" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                <p>No summary available yet</p>
                {hasTranscript && (
                  <button className="placeholder-action" onClick={handleGenerateSummary}>
                    Generate Summary
                  </button>
                )}
              </div>
            )
          )}
        </div>
      </div>

      {hasRecording && (
        <footer className="audio-player-footer">
          <AudioPlayer 
            ref={audioPlayerRef}
            audioUrl={`${API_BASE_URL}/api/meetings/${meetingId}/audio`}
            onTimeUpdate={setCurrentTime}
          />
        </footer>
      )}
    </div>
  );
};

export default MeetingDetail;
