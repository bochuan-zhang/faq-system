import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TicketsView = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/tickets');
      setTickets(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching tickets:', err);
      setError('Failed to load tickets. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="tickets-container">
        <div className="tickets-header">
          Support Tickets
        </div>
        <div className="loading">
          Loading tickets...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tickets-container">
        <div className="tickets-header">
          Support Tickets
        </div>
        <div className="error">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="tickets-container">
      <div className="tickets-header">
        Support Tickets ({tickets.length})
      </div>
      
      <div className="tickets-list">
        {tickets.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#7f8c8d' }}>
            No tickets found. Tickets will appear here when the AI creates them for unanswered questions.
          </div>
        ) : (
          tickets.map((ticket) => (
            <div key={ticket.id} className="ticket-item">
              <div className="ticket-header">
                <span className="ticket-id">Ticket #{ticket.id}</span>
                <span className="ticket-timestamp">
                  {formatTimestamp(ticket.timestamp)}
                </span>
              </div>
              
              <div className="ticket-question">
                <strong>Question:</strong> {ticket.user_question}
              </div>
              
              {ticket.user_contact && (
                <div className="ticket-contact">
                  <strong>Contact:</strong> {ticket.user_contact}
                </div>
              )}
              
              <div className="ticket-status open">
                {ticket.status}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TicketsView; 