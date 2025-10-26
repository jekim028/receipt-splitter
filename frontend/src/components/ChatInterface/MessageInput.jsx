/**
 * Message input component
 */
import { useState } from 'react';
import './ChatInterface.css';

export const MessageInput = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className="message-input-container" onSubmit={handleSubmit}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your message... (e.g., 'I had the burger')"
        className="message-input"
        disabled={disabled}
      />
      <button
        type="submit"
        className="send-button"
        disabled={!message.trim() || disabled}
      >
        Send
      </button>
    </form>
  );
};
