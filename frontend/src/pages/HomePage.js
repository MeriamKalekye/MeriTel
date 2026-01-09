import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <nav className="home-nav">
        <div className="nav-brand">
          <span className="logo">MeriTel</span>
        </div>
        <div className="nav-actions">
          <button className="btn-text" onClick={() => navigate('/meetings')}>
            My Meetings
          </button>
          <button className="btn-primary" onClick={() => navigate('/join-live')}>
            Get Started
          </button>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Your AI Meeting Assistant
          </h1>
          <p className="hero-subtitle">
            Join meetings automatically, capture every conversation, and get intelligent transcripts with AI-powered summaries
          </p>
          <div className="hero-actions">
            <button className="btn-hero-primary" onClick={() => navigate('/join-live')}>
              Join Live Meeting
            </button>
            <button className="btn-hero-secondary" onClick={() => navigate('/create')}>
              Upload Recording
            </button>
          </div>
          <p className="hero-platforms">
            Works with Google Meet, Zoom, and Microsoft Teams
          </p>
        </div>
      </section>

      <section className="features">
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon bot">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="10" rx="2" />
                <circle cx="12" cy="5" r="2" />
                <path d="M12 7v4" />
                <line x1="8" y1="16" x2="8" y2="16" />
                <line x1="16" y1="16" x2="16" y2="16" />
              </svg>
            </div>
            <h3>Automated Bot Joins</h3>
            <p>Our AI bot joins your meetings automatically, appearing as a participant to record everything seamlessly</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon transcript">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <line x1="10" y1="9" x2="8" y2="9" />
              </svg>
            </div>
            <h3>Smart Transcription</h3>
            <p>Get word-level timestamps and automatic speaker identification powered by advanced AI transcription</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon summary">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 20h9" />
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
              </svg>
            </div>
            <h3>AI Summaries</h3>
            <p>Automatically generate structured meeting notes with overview, action items, and key discussion points</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon real-time">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
            <h3>Real-time Updates</h3>
            <p>Watch transcripts appear live during meetings with synchronized audio playback and highlighting</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon multi-platform">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="7" width="20" height="14" rx="2" />
                <path d="M16 3h5v5" />
                <line x1="21" y1="3" x2="16" y2="8" />
              </svg>
            </div>
            <h3>Multi-Platform</h3>
            <p>Compatible with all major video conferencing platforms including Google Meet, Zoom, and Teams</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon dashboard">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7" />
                <rect x="14" y="3" width="7" height="7" />
                <rect x="14" y="14" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" />
              </svg>
            </div>
            <h3>Meeting Dashboard</h3>
            <p>Organize and access all your recordings, transcripts, and summaries in one beautiful interface</p>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="cta-content">
          <h2>Ready to transform your meetings?</h2>
          <p>Start recording, transcribing, and summarizing your meetings today</p>
          <button className="btn-cta" onClick={() => navigate('/join-live')}>
            Get Started Free
          </button>
        </div>
      </section>

      <footer className="home-footer">
        <p>© 2026 MeriTel. AI-powered meeting intelligence.</p>
      </footer>
    </div>
  );
};

export default HomePage;
