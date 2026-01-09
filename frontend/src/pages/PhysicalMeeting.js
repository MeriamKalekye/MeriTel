import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './PhysicalMeeting.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const PhysicalMeeting = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });

      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.start(1000);
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (err) {
      setError('Could not access microphone. Please grant permission.');
      console.error('Recording error:', err);
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      clearInterval(timerRef.current);
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    }
  };

  const stopRecording = () => {
    return new Promise((resolve) => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          
          mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
          clearInterval(timerRef.current);
          
          resolve(audioBlob);
        };

        mediaRecorderRef.current.stop();
        setIsRecording(false);
        setIsPaused(false);
      }
    });
  };

  const handleSaveRecording = async () => {
    if (!title.trim()) {
      setError('Please enter a meeting title');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const audioBlob = await stopRecording();

      const meetingResponse = await axios.post(`${API_BASE_URL}/api/meetings`, {
        title: title,
        description: description,
        meeting_type: 'physical',
        platform: 'recording',
        status: 'created'
      });

      const meetingId = meetingResponse.data.meeting.meeting_id;

      const formData = new FormData();
      formData.append('audio', audioBlob, `recording_${meetingId}.webm`);

      await axios.post(
        `${API_BASE_URL}/api/meetings/${meetingId}/upload`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );

      navigate(`/meetings/${meetingId}`);
    } catch (err) {
      console.error('Error saving recording:', err);
      setError(err.response?.data?.error || 'Failed to save recording');
      setIsProcessing(false);
    }
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

  const handleUploadSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Please enter a meeting title');
      return;
    }

    if (!uploadedFile) {
      setError('Please select an audio file');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const meetingResponse = await axios.post(`${API_BASE_URL}/api/meetings`, {
        title: title,
        description: description,
        meeting_type: 'physical',
        platform: 'upload',
        status: 'created'
      });

      const meetingId = meetingResponse.data.meeting.meeting_id;

      const formData = new FormData();
      formData.append('audio', uploadedFile);

      await axios.post(
        `${API_BASE_URL}/api/meetings/${meetingId}/upload`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );

      navigate(`/meetings/${meetingId}`);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError(err.response?.data?.error || 'Failed to upload file');
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!mode) {
    return (
      <div className="physical-meeting-page">
        <div className="physical-meeting-container">
          <button className="back-button" onClick={() => navigate('/')}>
            ← Back to Home
          </button>

          <div className="mode-selection">
            <h1>Physical Meeting</h1>
            <p className="subtitle">Choose how you want to capture your meeting</p>

            <div className="mode-cards">
              <div className="mode-card" onClick={() => setMode('record')}>
                <div className="mode-icon record">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <circle cx="12" cy="12" r="3" fill="currentColor"/>
                  </svg>
                </div>
                <h3>Record Now</h3>
                <p>Start recording your meeting right now</p>
              </div>

              <div className="mode-card" onClick={() => setMode('upload')}>
                <div className="mode-icon upload">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                </div>
                <h3>Upload Recording</h3>
                <p>Upload an existing audio or video file</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'record') {
    return (
      <div className="physical-meeting-page">
        <div className="physical-meeting-container">
          <button className="back-button" onClick={() => setMode(null)}>
            ← Back
          </button>

          <div className="recording-interface">
            <h1>Record Meeting</h1>
            
            <div className="form-group">
              <label>Meeting Title *</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Team Discussion, Client Meeting"
                disabled={isRecording}
              />
            </div>

            <div className="form-group">
              <label>Description (Optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add meeting notes or agenda"
                rows="3"
                disabled={isRecording}
              />
            </div>

            <div className="recording-controls">
              {!isRecording && recordingTime === 0 && (
                <button className="btn-record" onClick={startRecording}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="8"/>
                  </svg>
                  Start Recording
                </button>
              )}

              {isRecording && (
                <>
                  <div className="recording-status">
                    <div className="recording-indicator"></div>
                    <span className="recording-time">{formatTime(recordingTime)}</span>
                  </div>

                  <div className="recording-actions">
                    {!isPaused ? (
                      <button className="btn-pause" onClick={pauseRecording}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                          <rect x="6" y="4" width="4" height="16"/>
                          <rect x="14" y="4" width="4" height="16"/>
                        </svg>
                        Pause
                      </button>
                    ) : (
                      <button className="btn-resume" onClick={resumeRecording}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                          <polygon points="5 3 19 12 5 21"/>
                        </svg>
                        Resume
                      </button>
                    )}

                    <button className="btn-stop" onClick={handleSaveRecording} disabled={isProcessing}>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <rect x="4" y="4" width="16" height="16" rx="2"/>
                      </svg>
                      {isProcessing ? 'Saving...' : 'Stop & Save'}
                    </button>
                  </div>
                </>
              )}

              {!isRecording && recordingTime > 0 && !isProcessing && (
                <button className="btn-save" onClick={handleSaveRecording}>
                  Save Recording
                </button>
              )}
            </div>

            {error && <div className="error-message">{error}</div>}
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'upload') {
    return (
      <div className="physical-meeting-page">
        <div className="physical-meeting-container">
          <button className="back-button" onClick={() => setMode(null)}>
            ← Back
          </button>

          <form className="upload-form" onSubmit={handleUploadSubmit}>
            <h1>Upload Recording</h1>

            <div className="form-group">
              <label>Meeting Title *</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Team Discussion, Client Meeting"
                required
              />
            </div>

            <div className="form-group">
              <label>Description (Optional)</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add meeting notes or agenda"
                rows="3"
              />
            </div>

            <div className="form-group">
              <label>Audio/Video File *</label>
              <div className="file-upload-area">
                <input
                  type="file"
                  accept="audio/*,video/*,.mp3,.wav,.m4a,.mp4,.mov"
                  onChange={handleFileUpload}
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="file-upload-label">
                  {uploadedFile ? (
                    <div className="file-selected">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                        <polyline points="13 2 13 9 20 9"/>
                      </svg>
                      <div>
                        <span className="file-name">{uploadedFile.name}</span>
                        <span className="file-size">
                          ({(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB)
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="file-placeholder">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="17 8 12 3 7 8"/>
                        <line x1="12" y1="3" x2="12" y2="15"/>
                      </svg>
                      <p>Click to select or drag and drop</p>
                      <span>MP3, WAV, MP4, MOV, M4A (max 500MB)</span>
                    </div>
                  )}
                </label>
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button 
              type="submit" 
              className="btn-submit"
              disabled={isProcessing || !uploadedFile}
            >
              {isProcessing ? 'Uploading...' : 'Upload & Transcribe'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return null;
};

export default PhysicalMeeting;
