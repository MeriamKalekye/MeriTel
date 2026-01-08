import React from 'react';
import ActionItemsList from './ActionItemsList';
import MeetingOutline from './MeetingOutline';
import './StructuredSummary.css';

const StructuredSummary = ({ summary, onSeek, onToggleActionItem }) => {
  if (!summary) {
    return (
      <div className="structured-summary empty">
        <p>No summary available yet</p>
      </div>
    );
  }
  
  return (
    <div className="structured-summary">
      {summary.overview && (
        <section className="summary-section overview-section">
          <div className="section-header">
            <span className="section-icon">📝</span>
            <h3>Overview</h3>
          </div>
          <div className="overview-text">
            {typeof summary.overview === 'string' ? (
              <p>{summary.overview}</p>
            ) : (
              <p>{summary.overview.text}</p>
            )}
          </div>
        </section>
      )}
      
      {summary.action_items && summary.action_items.length > 0 && (
        <section className="summary-section action-items-section">
          <div className="section-header">
            <span className="section-icon">✅</span>
            <h3>Action Items</h3>
            <span className="section-count">{summary.action_items.length}</span>
          </div>
          <ActionItemsList 
            actionItems={summary.action_items}
            onToggle={onToggleActionItem}
          />
        </section>
      )}
      
      {summary.outline && summary.outline.length > 0 && (
        <section className="summary-section outline-section">
          <div className="section-header">
            <span className="section-icon">📋</span>
            <h3>Outline</h3>
            <span className="section-count">{summary.outline.length} topics</span>
          </div>
          <MeetingOutline 
            outline={summary.outline}
            onSeek={onSeek}
          />
        </section>
      )}
      
      {summary.keywords && summary.keywords.length > 0 && (
        <section className="summary-section keywords-section">
          <div className="section-header">
            <span className="section-icon">🏷️</span>
            <h3>Keywords</h3>
          </div>
          <div className="keywords-list">
            {summary.keywords.map((keyword, idx) => (
              <span key={idx} className="keyword-tag">{keyword}</span>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

export default StructuredSummary;
