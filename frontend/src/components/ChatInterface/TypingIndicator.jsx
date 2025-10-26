/**
 * Typing indicator component
 */
import './ChatInterface.css';

export const TypingIndicator = () => {
  return (
    <div className="message assistant">
      <div className="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
};
