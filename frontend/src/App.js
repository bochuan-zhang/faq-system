import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ChatInterface from './components/ChatInterface';
import TicketsView from './components/TicketsView';
import './App.css';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  // Chat state moved to App level for persistence
  const [messages, setMessages] = useState([]);
  const [userContact, setUserContact] = useState('');
  const [showEmailInput, setShowEmailInput] = useState(true);
  const [emailSubmitted, setEmailSubmitted] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(new Set());

  useEffect(() => {
    // Update localStorage when theme changes
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    // Update body class for global theme
    document.body.className = isDarkMode ? 'dark-mode' : 'light-mode';
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <Router>
      <div className={`App ${isDarkMode ? 'dark' : 'light'}`}>
        <nav className="navbar">
          <div className="nav-container">
            <h1 className="nav-title">FAQ System</h1>
            <div className="nav-links">
              <Link to="/" className="nav-link">Chat</Link>
              <Link to="/tickets" className="nav-link">Tickets</Link>
              <button 
                className="theme-toggle"
                onClick={toggleTheme}
                aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDarkMode ? '☀️' : '🌙'}
              </button>
            </div>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={
              <ChatInterface 
                messages={messages}
                setMessages={setMessages}
                userContact={userContact}
                setUserContact={setUserContact}
                showEmailInput={showEmailInput}
                setShowEmailInput={setShowEmailInput}
                emailSubmitted={emailSubmitted}
                setEmailSubmitted={setEmailSubmitted}
                feedbackSubmitted={feedbackSubmitted}
                setFeedbackSubmitted={setFeedbackSubmitted}
              />
            } />
            <Route path="/tickets" element={<TicketsView />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 