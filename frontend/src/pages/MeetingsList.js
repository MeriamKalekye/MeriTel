import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './MeetingsList.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const MeetingsList = () => {
  const navigate = useNavigate();
  const [meetings, setMeetings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadMeetings();
  }, []);

  const loadMeetings = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/meetings`);
      setMeetings(response.data.meetings || []);
    } catch (err) {
      console.error('Error loading meetings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (meeting) => {
    if (meeting.status === 'live') return <span className="status-badge live">Live</span>;
    if (meeting.transcript_file_path) return <span className="status-badge completed">Transcribed</span>;
    if (meeting.audio_file_path) return <span className="status-badge recorded">Recorded</span>;
    return <span className="status-badge scheduled">Scheduled</span>;
  };

  const filteredMeetings = meetings.filter(meeting => {
    if (filter === 'all') return true;
    if (filter === 'live') return meeting.status === 'live';
    if (filter === 'recorded') return meeting.audio_file_path && !meeting.transcript_file_path;
    if (filter === 'transcribed') return meeting.transcript_file_path;
    return true;
  });

  if (isLoading) {
    return (
      <div className="meetings-list-loading">
        <div className="loading-spinner"></div>
        <p>Loading meetings...</p>
      </div>
    );
  }

  return (
    <div className="meetings-list-page">
      <header className="meetings-header">
        <h1>My Meetings</h1>
        <div className="header-actions">
          <button className="btn-primary" onClick={() => navigate('/create')}>
            + New Meeting
          </button>
          <button className="btn-secondary" onClick={() => navigate('/join-live')}>
            🔴 Join Live Meeting
          </button>
        </div>
      </header>

      <div className="filter-tabs">
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All ({meetings.length})
        </button>
        <button 
          className={filter === 'live' ? 'active' : ''}
          onClick={() => setFilter('live')}
        >
          Live ({meetings.filter(m => m.status === 'live').length})
        </button>
        <button 
          className={filter === 'recorded' ? 'active' : ''}
          onClick={() => setFilter('recorded')}
        >
          Recorded ({meetings.filter(m => m.audio_file_path && !m.transcript_file_path).length})
        </button>
        <button 
          className={filter === 'transcribed' ? 'active' : ''}
          onClick={() => setFilter('transcribed')}
        >
          Transcribed ({meetings.filter(m => m.transcript_file_path).length})
        </button>
      </div>

      <div className="meetings-grid">
        {filteredMeetings.length === 0 ? (
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
              <rect x="12" y="16" width="40" height="32" rx="2" stroke="#ccc" strokeWidth="2"/>
              <circle cx="22" cy="28" r="3" fill="#ccc"/>
              <circle cx="32" cy="28" r="3" fill="#ccc"/>
              <circle cx="42" cy="28" r="3" fill="#ccc"/>
            </svg>
            <h3>No meetings found</h3>
            <p>Create a new meeting or join a live one to get started</p>
            <button className="btn-primary" onClick={() => navigate('/create')}>
              Create Meeting
            </button>
          </div>
        ) : (
          filteredMeetings.map(meeting => (
            <div 
              key={meeting.meeting_id}
              className="meeting-card"
              onClick={() => navigate(`/meetings/${meeting.meeting_id}`)}
            >
              <div className="meeting-card-header">
                <h3>{meeting.title}</h3>
                {getStatusBadge(meeting)}
              </div>
              
              {meeting.description && (
                <p className="meeting-description">{meeting.description}</p>
              )}
              
              <div className="meeting-meta">
                <span className="meta-item">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <rect x="2" y="3" width="10" height="9" rx="1" stroke="currentColor" strokeWidth="1.5"/>
                    <path d="M4 1v2M10 1v2M2 5h10" stroke="currentColor" strokeWidth="1.5"/>
                  </svg>
                  {new Date(meeting.created_at).toLocaleDateString()}
                </span>
                
                {meeting.duration > 0 && (
                  <span className="meta-item">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/>
                      <path d="M7 3v4l2.5 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                    </svg>
                    {Math.floor(meeting.duration / 60)}m
                  </span>
                )}
                
                <span className="meta-item">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="5" r="2" stroke="currentColor" strokeWidth="1.5"/>
                    <path d="M2 12c0-2.5 2-4 5-4s5 1.5 5 4" stroke="currentColor" strokeWidth="1.5"/>
                  </svg>
                  {meeting.participants?.length || 0}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MeetingsList;
