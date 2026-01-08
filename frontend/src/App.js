import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import CreateMeeting from './pages/CreateMeeting';
import MeetingDetail from './pages/MeetingDetail';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<CreateMeeting />} />
        <Route path="/meetings/:meetingId" element={<MeetingDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
