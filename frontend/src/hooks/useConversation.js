/**
 * Hook for managing conversation state and messaging
 */
import { useState, useCallback } from 'react';
import { sendMessage, getMessages } from '../utils/api';

export const useConversation = (conversationId) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Send a message to the agent
   */
  const send = useCallback(async (messageText) => {
    if (!conversationId || !messageText.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message optimistically
    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendMessage(conversationId, messageText);

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      return response; // Return the full response including assignment_state and highlighted_items
    } catch (err) {
      setError(err.message || 'Failed to send message');
      // Remove the optimistic user message on error
      setMessages((prev) => prev.slice(0, -1));
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  /**
   * Refresh messages from the server
   */
  const refresh = useCallback(async () => {
    if (!conversationId) return;

    try {
      const data = await getMessages(conversationId);
      setMessages(data.messages || []);
    } catch (err) {
      setError(err.message || 'Failed to load messages');
    }
  }, [conversationId]);

  return {
    messages,
    setMessages,
    send,
    refresh,
    isLoading,
    error,
  };
};
