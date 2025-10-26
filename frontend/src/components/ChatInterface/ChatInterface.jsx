/**
 * Main chat interface container
 */
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import './ChatInterface.css';

export const ChatInterface = ({ messages, onSendMessage, isLoading }) => {
  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>Chat with AI Assistant</h3>
        <p>Tell me who ordered what, and I'll split the bill</p>
      </div>

      <MessageList messages={messages} isLoading={isLoading} />

      <MessageInput onSend={onSendMessage} disabled={isLoading} />
    </div>
  );
};
