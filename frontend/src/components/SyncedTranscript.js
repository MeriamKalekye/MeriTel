import React, { useEffect, useRef } from 'react';
import { findCurrentSegment, findCurrentWord, formatTime } from '../utils/transcriptHighlighter';
import './SyncedTranscript.css';

const SyncedTranscript = ({ segments, currentTime, onSeek }) => {
  const currentSegmentIndex = findCurrentSegment(segments, currentTime);
  const activeRef = useRef(null);
  const containerRef = useRef(null);
  
  useEffect(() => {
    if (activeRef.current && containerRef.current) {
      const container = containerRef.current;
      const element = activeRef.current;
      
      const containerRect = container.getBoundingClientRect();
      const elementRect = element.getBoundingClientRect();
      
      if (elementRect.top < containerRect.top || elementRect.bottom > containerRect.bottom) {
        element.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }
    }
  }, [currentSegmentIndex]);
  
  if (!segments || segments.length === 0) {
    return (
      <div className="synced-transcript empty">
        <p>No transcript available</p>
      </div>
    );
  }
  
  return (
    <div className="synced-transcript" ref={containerRef}>
      {segments.map((segment, index) => {
        const isActive = index === currentSegmentIndex;
        const currentWordIndex = isActive 
          ? findCurrentWord(segment, currentTime) 
          : -1;
        
        return (
          <div 
            key={segment.segment_id || index}
            className={`transcript-segment ${isActive ? 'active' : ''}`}
            ref={isActive ? activeRef : null}
            onClick={() => onSeek && onSeek(segment.start_time)}
          >
            <div className="speaker-info">
              <div className="speaker-avatar">
                {segment.speaker_name ? segment.speaker_name.charAt(0).toUpperCase() : '?'}
              </div>
              <div className="speaker-details">
                <span className="speaker-name">{segment.speaker_name || 'Unknown Speaker'}</span>
                <span className="timestamp">{formatTime(segment.start_time)}</span>
              </div>
            </div>
            <div className="segment-text">
              {segment.words && segment.words.length > 0 ? (
                segment.words.map((word, wIdx) => (
                  <span 
                    key={wIdx}
                    className={`word ${wIdx === currentWordIndex ? 'highlight-word' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSeek && onSeek(word.start);
                    }}
                  >
                    {word.word}{' '}
                  </span>
                ))
              ) : (
                <span>{segment.text}</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SyncedTranscript;
