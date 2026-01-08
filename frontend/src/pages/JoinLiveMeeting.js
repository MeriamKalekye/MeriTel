import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './JoinLiveMeeting.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const JoinLiveMeeting = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    meetingUrl: '',
    botName: 'MeriTel Bot'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const detectPlatform = (url) => {
    if (url.includes('meet.google.com')) return 'Google Meet';
    if (url.includes('zoom.us')) return 'Zoom';
    if (url.includes('teams.microsoft.com')) return 'Microsoft Teams';
    return 'Unknown';
  };

  const validateMeetingUrl = (url) => {
    const validPatterns = [
      /meet\.google\.com/,
      /zoom\.us\/j\//,
      /teams\.microsoft\.com/
    ];
    return validPatterns.some(pattern => pattern.test(url));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.title.trim()) {
      setError('Meeting title is required');
      return;
    }

    if (!formData.meetingUrl.trim()) {
      setError('Meeting URL is required');
      return;
    }

    if (!validateMeetingUrl(formData.meetingUrl)) {
      setError('Invalid meeting URL. Please enter a valid Google Meet, Zoom, or Teams link');
      return;
    }

    setIsLoading(true);

    try {
      const meetingData = {
        title: formData.title,
        description: formData.description,
        meeting_type: 'online',
        platform: detectPlatform(formData.meetingUrl).toLowerCase().replace(' ', ''),
        join_url: formData.meetingUrl,
        status: 'scheduled'
      };

      const meetingResponse = await axios.post(`${API_BASE_URL}/api/meetings`, meetingData);
      const meetingId = meetingResponse.data.meeting.meeting_id;

      const botResponse = await axios.post(`${API_BASE_URL}/api/bots/start`, {
        meeting_id: meetingId,
        meeting_url: formData.meetingUrl,
        bot_name: formData.botName
      });

      if (botResponse.status === 200) {
        navigate(`/meetings/${meetingId}/live`);
      }
    } catch (err) {
      console.error('Error joining meeting:', err);
      setError(err.response?.data?.error || 'Failed to join meeting. Please try again.');
      setIsLoading(false);
    }
  };

  const platform = detectPlatform(formData.meetingUrl);

  return (
    <div className="join-live-meeting">
      <div className="join-header">
        <button className="back-button" onClick={() => navigate('/')}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back
        </button>
        <h1>Join Live Meeting</h1>
        <p className="subtitle">Send MeriTel bot to record, transcribe, and summarize your meeting</p>
      </div>

      <form className="join-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Meeting Title *</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="e.g., Weekly Team Sync"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description (Optional)</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Add meeting notes or agenda"
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="meetingUrl">Meeting Link *</label>
          <input
            type="url"
            id="meetingUrl"
            name="meetingUrl"
            value={formData.meetingUrl}
            onChange={handleInputChange}
            placeholder="https://meet.google.com/abc-defg-hij or https://zoom.us/j/123456789"
            required
          />
          {formData.meetingUrl && platform !== 'Unknown' && (
            <div className="platform-badge">
              <span className={`badge ${platform.toLowerCase().replace(' ', '-')}`}>
                {platform}
              </span>
            </div>
          )}
          <small className="help-text">
            Supported: Google Meet, Zoom, Microsoft Teams
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="botName">Bot Display Name</label>
          <input
            type="text"
            id="botName"
            name="botName"
            value={formData.botName}
            onChange={handleInputChange}
            placeholder="MeriTel Bot"
          />
          <small className="help-text">
            This name will appear in the meeting participant list
          </small>
        </div>

        {error && (
          <div className="error-message">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2"/>
              <path d="M10 6v4M10 14v.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            {error}
          </div>
        )}

        <div className="form-actions">
          <button
            type="submit"
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="spinner"></div>
                Starting Bot...
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M10 2v16M18 10H2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Join with Bot
              </>
            )}
          </button>
        </div>
      </form>

      <div className="info-section">
        <h3>How it works</h3>
        <ol className="steps-list">
          <li>
            <strong>Enter meeting details</strong> - Provide the meeting title and link
          </li>
          <li>
            <strong>Bot joins automatically</strong> - MeriTel bot joins as a participant
          </li>
          <li>
            <strong>Real-time transcription</strong> - See live transcript as people speak
          </li>
          <li>
            <strong>AI-powered summary</strong> - Get action items and meeting outline after
          </li>
        </ol>
      </div>
    </div>
  );
};

export default JoinLiveMeeting;
