import React from 'react';
import './ActionItemsList.css';

const ActionItemsList = ({ actionItems, onToggle }) => {
  if (!actionItems || actionItems.length === 0) {
    return (
      <div className="action-items-empty">
        <p>No action items identified</p>
      </div>
    );
  }
  
  return (
    <div className="action-items-list">
      {actionItems.map((item, index) => (
        <div key={item.id || index} className={`action-item ${item.completed ? 'completed' : ''}`}>
          <input 
            type="checkbox" 
            checked={item.completed || false}
            onChange={() => onToggle && onToggle(item.id || index)}
            className="action-checkbox"
          />
          <div className="action-content">
            <p className="action-text">{item.text}</p>
            <div className="action-meta">
              {item.assignee && (
                <span className="assignee">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M7 7C8.65685 7 10 5.65685 10 4C10 2.34315 8.65685 1 7 1C5.34315 1 4 2.34315 4 4C4 5.65685 5.34315 7 7 7Z" stroke="currentColor" strokeWidth="1.5"/>
                    <path d="M1 13C1 10.2386 3.23858 8 6 8H8C10.7614 8 13 10.2386 13 13" stroke="currentColor" strokeWidth="1.5"/>
                  </svg>
                  {item.assignee}
                </span>
              )}
              {item.deadline && (
                <span className="deadline">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="7" r="6" stroke="currentColor" strokeWidth="1.5"/>
                    <path d="M7 3.5V7H10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                  </svg>
                  Due: {item.deadline}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ActionItemsList;
