import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CreateMeeting from './pages/CreateMeeting';
import MeetingDetail from './pages/MeetingDetail';
import JoinLiveMeeting from './pages/JoinLiveMeeting';
import LiveMeeting from './pages/LiveMeeting';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<CreateMeeting />} />
        <Route path="/join-live" element={<JoinLiveMeeting />} />
        <Route path="/meetings/:meetingId" element={<MeetingDetail />} />
        <Route path="/meetings/:meetingId/live" element={<LiveMeeting />} />
      </Routes>
    </Router>
  );
}

export default App;
