import React, { useState } from 'react';
import { formatDuration, formatTime } from '../utils/transcriptHighlighter';
import './MeetingOutline.css';

const MeetingOutline = ({ outline, onSeek }) => {
  const [expanded, setExpanded] = useState({});
  
  const toggle = (topicId) => {
    setExpanded(prev => ({ ...prev, [topicId]: !prev[topicId] }));
  };
  
  if (!outline || outline.length === 0) {
    return (
      <div className="meeting-outline-empty">
        <p>No outline available</p>
      </div>
    );
  }
  
  return (
    <div className="meeting-outline">
      {outline.map((topic, idx) => {
        const topicId = topic.id || idx;
        const isExpanded = expanded[topicId];
        
        return (
          <div key={topicId} className="outline-topic">
            <div 
              className="topic-header"
              onClick={() => toggle(topicId)}
            >
              <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                ▶
              </span>
              <div className="topic-info">
                <span className="topic-title">{topic.topic || `Topic ${idx + 1}`}</span>
                <span className="topic-metadata">
                  {topic.timestamp !== undefined && (
                    <span className="topic-time">
                      {formatTime(topic.timestamp)}
                    </span>
                  )}
                  {topic.duration !== undefined && (
                    <span className="topic-duration">
                      • {formatDuration(topic.duration)}
                    </span>
                  )}
                </span>
              </div>
              {topic.timestamp !== undefined && (
                <button
                  className="seek-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSeek && onSeek(topic.timestamp);
                  }}
                  title="Jump to this section"
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M4 3L12 8L4 13V3Z" fill="currentColor"/>
                  </svg>
                </button>
              )}
            </div>
            {isExpanded && topic.subtopics && topic.subtopics.length > 0 && (
              <ul className="subtopics">
                {topic.subtopics.map((sub, subIdx) => (
                  <li key={subIdx} className="subtopic">
                    <span className="subtopic-bullet">•</span>
                    {sub}
                  </li>
                ))}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default MeetingOutline;
