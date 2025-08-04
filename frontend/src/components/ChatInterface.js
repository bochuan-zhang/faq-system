import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const ChatInterface = ({ 
  messages, 
  setMessages, 
  userContact, 
  setUserContact, 
  showEmailInput, 
  setShowEmailInput, 
  emailSubmitted, 
  setEmailSubmitted, 
  feedbackSubmitted, 
  setFeedbackSubmitted 
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generatePDF = async () => {
    if (messages.length === 0) {
      alert('No messages to download.');
      return;
    }

    setIsGeneratingPDF(true);
    
    try {
      // Create a temporary container for the PDF content
      const pdfContainer = document.createElement('div');
      pdfContainer.style.position = 'absolute';
      pdfContainer.style.left = '-9999px';
      pdfContainer.style.top = '0';
      pdfContainer.style.width = '800px';
      pdfContainer.style.padding = '20px';
      pdfContainer.style.backgroundColor = 'white';
      pdfContainer.style.fontFamily = 'Arial, sans-serif';
      pdfContainer.style.fontSize = '12px';
      pdfContainer.style.lineHeight = '1.4';
      
      // Add header
      const header = document.createElement('div');
      header.innerHTML = `
        <h1 style="color: #2c3e50; margin-bottom: 10px; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
          FAQ System Chat Transcript
        </h1>
        <p style="color: #7f8c8d; margin-bottom: 20px;">
          Generated on: ${new Date().toLocaleString()}
          ${userContact ? `<br>User Contact: ${userContact}` : ''}
        </p>
      `;
      pdfContainer.appendChild(header);
      
      // Add messages
      messages.forEach((message, index) => {
        const messageDiv = document.createElement('div');
        messageDiv.style.marginBottom = '15px';
        messageDiv.style.padding = '10px';
        messageDiv.style.borderRadius = '8px';
        messageDiv.style.maxWidth = '100%';
        
        if (message.sender === 'user') {
          messageDiv.style.backgroundColor = '#3498db';
          messageDiv.style.color = 'white';
          messageDiv.style.textAlign = 'right';
          messageDiv.style.marginLeft = '20%';
        } else {
          messageDiv.style.backgroundColor = '#ecf0f1';
          messageDiv.style.color = '#2c3e50';
          messageDiv.style.textAlign = 'left';
          messageDiv.style.marginRight = '20%';
        }
        
        messageDiv.innerHTML = `
          <div style="font-weight: bold; margin-bottom: 5px;">
            ${message.sender === 'user' ? 'You' : 'Assistant'}
          </div>
          <div>${message.text}</div>
          <div style="font-size: 10px; margin-top: 5px; opacity: 0.7;">
            ${new Date(message.timestamp).toLocaleString()}
          </div>
        `;
        
        pdfContainer.appendChild(messageDiv);
      });
      
      // Add footer
      const footer = document.createElement('div');
      footer.innerHTML = `
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 10px;">
          <p>This transcript was generated from the FAQ System chat interface.</p>
          <p>Total messages: ${messages.length}</p>
        </div>
      `;
      pdfContainer.appendChild(footer);
      
      document.body.appendChild(pdfContainer);
      
      // Convert to canvas
      const canvas = await html2canvas(pdfContainer, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
      });
      
      // Remove temporary container
      document.body.removeChild(pdfContainer);
      
      // Create PDF
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = pdfWidth - 20; // 10mm margin on each side
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      let heightLeft = imgHeight;
      let position = 10; // 10mm top margin
      
      // Add first page
      pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
      heightLeft -= (pdfHeight - 20);
      
      // Add additional pages if needed
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight + 10;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
        heightLeft -= (pdfHeight - 20);
      }
      
      // Download PDF
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      pdf.save(`chat-transcript-${timestamp}.pdf`);
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const submitFeedback = async (messageId, isHelpful, originalQuestion) => {
    try {
      const response = await axios.post('/feedback', {
        message_id: messageId,
        is_helpful: isHelpful,
        user_contact: userContact || null,
        original_question: originalQuestion
      });

      // Mark feedback as submitted for this message
      setFeedbackSubmitted(prev => new Set([...prev, messageId]));

      // Show feedback confirmation
      if (response.data.ticket_created) {
        const feedbackMessage = {
          id: Date.now() + Math.random(),
          text: "Thank you for your feedback. A support ticket has been created to improve our responses.",
          sender: 'system',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, feedbackMessage]);
      } else {
        const feedbackMessage = {
          id: Date.now() + Math.random(),
          text: "Thank you for your feedback!",
          sender: 'system',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, feedbackMessage]);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post('/chat', {
        message: inputMessage,
        user_contact: userContact || null
      });

      const assistantMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'assistant',
        timestamp: new Date(),
        ticketCreated: response.data.ticket_created,
        messageId: response.data.message_id,
        originalQuestion: inputMessage  // Store the original question
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Check for specific error types
      let errorText = 'Sorry, I encountered an error. Please try again.';
      
      if (error.response) {
        // Server responded with error status
        if (error.response.status === 429) {
          errorText = 'OpenAI API quota exceeded. Please try again later or contact support.';
        } else if (error.response.status === 500) {
          const errorDetail = error.response.data?.detail || '';
          if (errorDetail.includes('quota') || errorDetail.includes('insufficient_quota')) {
            errorText = 'OpenAI API quota exceeded. Please try again later or contact support.';
          } else {
            errorText = 'Server error. Please try again later.';
          }
        } else if (error.response.status === 404) {
          errorText = 'Service temporarily unavailable. Please try again later.';
        }
      } else if (error.request) {
        // Network error
        errorText = 'Network error. Please check your connection and try again.';
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        text: errorText,
        sender: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container" ref={chatContainerRef}>
      <div className="chat-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Customer Support Chat</span>
          {messages.length > 0 && (
            <button
              className="download-pdf-button"
              onClick={generatePDF}
              disabled={isGeneratingPDF}
              title="Download chat transcript as PDF"
            >
              {isGeneratingPDF ? '📄 Generating...' : '📄 Download PDF'}
            </button>
          )}
        </div>
      </div>
      
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-content">
              {message.text}
              {message.ticketCreated && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', opacity: 0.8 }}>
                  📋 A support ticket has been created for your question.
                </div>
              )}
              
              {/* Feedback buttons for assistant messages */}
              {message.sender === 'assistant' && message.messageId && !feedbackSubmitted.has(message.messageId) && (
                <div className="feedback-container">
                  <div className="feedback-question">Was this answer helpful?</div>
                  <div className="feedback-buttons">
                    <button
                      className="feedback-button feedback-yes"
                      onClick={() => submitFeedback(message.messageId, true, message.originalQuestion)}
                    >
                      👍 Yes
                    </button>
                    <button
                      className="feedback-button feedback-no"
                      onClick={() => submitFeedback(message.messageId, false, message.originalQuestion)}
                    >
                      👎 No
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                Thinking...
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        {showEmailInput && (
          <div className="contact-input">
            <label htmlFor="userContact">Email (optional):</label>
            <input
              id="userContact"
              type="email"
              placeholder="Enter your email for ticket notifications"
              value={userContact}
              onChange={(e) => setUserContact(e.target.value)}
              onBlur={() => {
                if (userContact.trim()) {
                  setShowEmailInput(false);
                  setEmailSubmitted(true);
                }
              }}
            />
            {userContact.trim() && (
              <button
                type="button"
                className="email-done-button"
                onClick={() => {
                  setShowEmailInput(false);
                  setEmailSubmitted(true);
                }}
              >
                Done
              </button>
            )}
          </div>
        )}
        
        {emailSubmitted && userContact.trim() && (
          <div className="email-success-message">
            <span className="email-success-icon">✓</span>
            <span className="email-success-text">Email saved: {userContact}</span>
            <button
              type="button"
              className="email-edit-button"
              onClick={() => {
                setShowEmailInput(true);
                setEmailSubmitted(false);
              }}
            >
              Edit
            </button>
          </div>
        )}
        
        <form onSubmit={sendMessage} className="chat-input-form">
          <input
            type="text"
            className="chat-input"
            placeholder="Type your question here..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-button"
            disabled={isLoading || !inputMessage.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface; 