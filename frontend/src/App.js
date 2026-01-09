import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import MeetingsList from './pages/MeetingsList';
import CreateMeeting from './pages/CreateMeeting';
import MeetingDetail from './pages/MeetingDetail';
import JoinLiveMeeting from './pages/JoinLiveMeeting';
import LiveMeeting from './pages/LiveMeeting';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/meetings" element={<MeetingsList />} />
        <Route path="/create" element={<CreateMeeting />} />
        <Route path="/join-live" element={<JoinLiveMeeting />} />
        <Route path="/meetings/:meetingId" element={<MeetingDetail />} />
        <Route path="/meetings/:meetingId/live" element={<LiveMeeting />} />
      </Routes>
    </Router>
  );
}

export default App;
