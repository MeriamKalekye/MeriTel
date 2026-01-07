import React, { useRef, useEffect } from 'react';
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
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  const handleProgressChange = (e) => {
    const newTime = parseFloat(e.target.value);
    seekTo(newTime);
  };
  
  const calculateProgress = () => {
    if (!duration || duration === 0) return 0;
    return (currentTime / duration) * 100;
  };
  
  return (
    <div className="audio-player">
      <audio ref={audioRef} src={audioUrl} />
      
      <button className="play-pause-btn" onClick={handlePlayPause}>
        {isPlaying ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M8 5v14l11-7z"/>
          </svg>
        )}
      </button>
      
      <div className="time-display">
        {formatTime(currentTime)}
      </div>
      
      <div className="progress-container">
        <input 
          type="range" 
          className="progress-bar"
          min="0" 
          max={duration || 0} 
          value={currentTime}
          onChange={handleProgressChange}
          style={{
            background: `linear-gradient(to right, #2196F3 0%, #2196F3 ${calculateProgress()}%, #ddd ${calculateProgress()}%, #ddd 100%)`
          }}
        />
      </div>
      
      <div className="time-display duration">
        {formatTime(duration)}
      </div>
    </div>
  );
};

export default AudioPlayer;
