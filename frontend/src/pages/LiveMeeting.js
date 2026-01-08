import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import io from 'socket.io-client';
import './LiveMeeting.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const LiveMeeting = () => {
  const { meetingId } = useParams();
  const navigate = useNavigate();
  const socketRef = useRef(null);
  const transcriptEndRef = useRef(null);
  
  const [meeting, setMeeting] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [transcriptSegments, setTranscriptSegments] = useState([]);
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isStopping, setIsStopping] = useState(false);

  useEffect(() => {
    loadMeetingData();
    connectWebSocket();
    
    const statusInterval = setInterval(fetchBotStatus, 5000);
    
    return () => {
      clearInterval(statusInterval);
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [meetingId]);

  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [transcriptSegments, interimTranscript]);

  const loadMeetingData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/meetings/${meetingId}`);
      setMeeting(response.data.meeting);
      setIsLoading(false);
    } catch (err) {
      console.error('Error loading meeting:', err);
      setError('Failed to load meeting');
      setIsLoading(false);
    }
  };

  const fetchBotStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/bots/${meetingId}/status`);
      setBotStatus(response.data);
      
      if (response.data.status === 'inactive') {
        navigate(`/meetings/${meetingId}`);
      }
    } catch (err) {
      console.error('Error fetching bot status:', err);
    }
  };

  const connectWebSocket = () => {
    socketRef.current = io(API_BASE_URL);
    
    socketRef.current.on('connect', () => {
      console.log('WebSocket connected');
      socketRef.current.emit('join_meeting', { meeting_id: meetingId });
    });
    
    socketRef.current.on('transcript_update', (data) => {
      if (data.meeting_id === meetingId) {
        handleTranscriptUpdate(data.transcript);
      }
    });
    
    socketRef.current.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });
  };

  const handleTranscriptUpdate = (transcript) => {
    if (transcript.is_final) {
      setTranscriptSegments(prev => [...prev, {
        text: transcript.text,
        words: transcript.words || [],
        timestamp: new Date().toISOString()
      }]);
      setInterimTranscript('');
    } else {
      setInterimTranscript(transcript.text);
    }
  };

  const handleStopBot = async () => {
    if (!window.confirm('Stop recording? The bot will leave the meeting and processing will begin.')) {
      return;
    }

    setIsStopping(true);
    try {
      await axios.post(`${API_BASE_URL}/api/bots/${meetingId}/stop`);
      navigate(`/meetings/${meetingId}`);
    } catch (err) {
      console.error('Error stopping bot:', err);
      setError('Failed to stop bot');
      setIsStopping(false);
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="live-meeting-loading">
        <div className="loading-spinner"></div>
        <p>Loading meeting...</p>
      </div>
    );
  }

  if (error && !meeting) {
    return (
      <div className="live-meeting-error">
        <p>{error}</p>
        <button onClick={() => navigate('/')}>Go Back</button>
      </div>
    );
  }

  return (
    <div className="live-meeting">
      <header className="live-header">
        <div className="live-status-bar">
          <div className="status-indicator">
            <span className="live-dot"></span>
            <span className="live-text">LIVE</span>
          </div>
          {botStatus && botStatus.duration > 0 && (
            <div className="duration">
              {formatDuration(botStatus.duration)}
            </div>
          )}
        </div>
        
        <div className="meeting-info">
          <h1>{meeting?.title}</h1>
          {meeting?.join_url && (
            <a href={meeting.join_url} target="_blank" rel="noopener noreferrer" className="meeting-link">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M14 9v3.5a1.5 1.5 0 01-1.5 1.5h-9A1.5 1.5 0 012 12.5v-9A1.5 1.5 0 013.5 2H7m4 0h3m0 0v3m0-3L7 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Join Meeting
            </a>
          )}
        </div>

        <button 
          className="stop-button"
          onClick={handleStopBot}
          disabled={isStopping}
        >
          {isStopping ? 'Stopping...' : 'Stop Recording'}
        </button>
      </header>

      <div className="live-content">
        <div className="transcript-panel">
          <div className="panel-header">
            <h2>Live Transcript</h2>
            <span className="segment-count">{transcriptSegments.length} segments</span>
          </div>
          
          <div className="transcript-stream">
            {transcriptSegments.length === 0 && !interimTranscript && (
              <div className="empty-state">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <rect x="20" y="12" width="24" height="40" rx="4" stroke="#ccc" strokeWidth="2"/>
                  <path d="M32 52v6M26 58h12" stroke="#ccc" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                <p>Waiting for audio...</p>
                <small>The bot is joining the meeting</small>
              </div>
            )}
            
            {transcriptSegments.map((segment, index) => (
              <div key={index} className="transcript-line">
                <div className="line-timestamp">
                  {new Date(segment.timestamp).toLocaleTimeString()}
                </div>
                <div className="line-text">{segment.text}</div>
              </div>
            ))}
            
            {interimTranscript && (
              <div className="transcript-line interim">
                <div className="line-timestamp">
                  {new Date().toLocaleTimeString()}
                </div>
                <div className="line-text">{interimTranscript}</div>
              </div>
            )}
            
            <div ref={transcriptEndRef} />
          </div>
        </div>

        <div className="info-panel">
          <div className="panel-section">
            <h3>Meeting Status</h3>
            <div className="status-grid">
              <div className="status-item">
                <span className="label">Status</span>
                <span className="value">
                  <span className="status-badge recording">Recording</span>
                </span>
              </div>
              <div className="status-item">
                <span className="label">Bot Status</span>
                <span className="value">{botStatus?.is_recording ? 'Active' : 'Connecting...'}</span>
              </div>
              <div className="status-item">
                <span className="label">Platform</span>
                <span className="value">{meeting?.platform || 'Unknown'}</span>
              </div>
            </div>
          </div>

          <div className="panel-section">
            <h3>Instructions</h3>
            <ol className="instructions-list">
              <li>The MeriTel bot has joined your meeting</li>
              <li>Speak normally - transcription happens in real-time</li>
              <li>Click "Stop Recording" when finished</li>
              <li>Processing will begin automatically after stopping</li>
            </ol>
          </div>

          {error && (
            <div className="error-banner">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveMeeting;
