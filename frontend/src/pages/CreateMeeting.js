import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './CreateMeeting.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const CreateMeeting = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    meeting_type: 'online',
    platform: 'upload'
  });
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 500 * 1024 * 1024) {
        setError('File size must be less than 500MB');
        return;
      }
      setUploadedFile(file);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      setError('Please enter a meeting title');
      return;
    }

    if (formData.platform === 'upload' && !uploadedFile) {
      setError('Please select an audio or video file to upload');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const meetingResponse = await axios.post(`${API_BASE_URL}/api/meetings`, {
        title: formData.title,
        description: formData.description,
        meeting_type: formData.meeting_type,
        platform: formData.platform,
        status: 'created'
      });

      const meeting = meetingResponse.data.meeting;
      const meetingId = meeting.meeting_id;

      if (formData.platform === 'upload' && uploadedFile) {
        const uploadFormData = new FormData();
        uploadFormData.append('audio', uploadedFile);

        await axios.post(
          `${API_BASE_URL}/api/meetings/${meetingId}/upload`,
          uploadFormData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              console.log(`Upload progress: ${percentCompleted}%`);
            }
          }
        );
      }

      navigate(`/meetings/${meetingId}`);
    } catch (err) {
      console.error('Error creating meeting:', err);
      setError(err.response?.data?.error || 'Failed to create meeting');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="create-meeting-page">
      <div className="create-meeting-container">
        <h1>Create New Meeting</h1>
        
        <form onSubmit={handleSubmit} className="meeting-form">
          <div className="form-group">
            <label htmlFor="title">Meeting Title *</label>
            <input
              id="title"
              name="title"
              type="text"
              placeholder="e.g., Team Standup, Client Review"
              value={formData.title}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              placeholder="Add meeting description (optional)"
              rows="3"
              value={formData.description}
              onChange={handleInputChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="platform">Source</label>
            <select
              id="platform"
              name="platform"
              value={formData.platform}
              onChange={handleInputChange}
            >
              <option value="upload">Upload Recording</option>
              <option value="zoom">Import from Zoom</option>
              <option value="meet">Import from Google Meet</option>
              <option value="teams">Import from Microsoft Teams</option>
            </select>
          </div>

          {formData.platform === 'upload' && (
            <div className="form-group">
              <label htmlFor="file-upload">Audio/Video File *</label>
              <div className="file-upload-wrapper">
                <input
                  id="file-upload"
                  type="file"
                  accept="audio/*,video/*"
                  onChange={handleFileUpload}
                  className="file-input"
                />
                <div className="file-upload-display">
                  {uploadedFile ? (
                    <div className="file-selected">
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M10 0C4.5 0 0 4.5 0 10s4.5 10 10 10 10-4.5 10-10S15.5 0 10 0zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8z" fill="#4CAF50"/>
                        <path d="M8 14l-4-4 1.4-1.4L8 11.2l6.6-6.6L16 6l-8 8z" fill="#4CAF50"/>
                      </svg>
                      <span>{uploadedFile.name}</span>
                      <span className="file-size">
                        ({(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB)
                      </span>
                    </div>
                  ) : (
                    <div className="file-placeholder">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="#2196F3"/>
                      </svg>
                      <span>Click to select file or drag and drop</span>
                      <span className="file-hint">Supported: MP3, WAV, MP4, MOV, M4A (max 500MB)</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {formData.platform !== 'upload' && (
            <div className="platform-connect-info">
              <p>Click "Create Meeting" to connect to {formData.platform} and import your recording.</p>
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? 'Creating...' : 'Create Meeting'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateMeeting;
