/**
 * API client for receipt splitter backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload a receipt image and get a processing token
 * @param {File} file - Receipt image file
 * @returns {Promise<{token: string, message: string}>}
 */
export const uploadReceipt = async (file) => {
  console.log('[API] Uploading receipt to /api/receipt/upload');
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/receipt/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  console.log('[API] Upload response:', response.data);
  return response.data;
};

/**
 * Poll for receipt processing results
 * @param {string} token - Processing token from upload
 * @returns {Promise<Object>} - Receipt data or processing status
 */
export const getReceiptResult = async (token) => {
  console.log(`[API] Polling receipt status for token: ${token}`);
  const response = await api.get(`/api/receipt/result/${token}`);
  console.log(`[API] Poll response:`, response.data);
  return response.data;
};

/**
 * Start a new conversation for receipt splitting
 * @param {Object} receipt - Parsed receipt data
 * @param {string[]} people - Array of person names
 * @returns {Promise<{conversation_id: string, message: string, assignment_state: Object}>}
 */
export const startConversation = async (receipt, people) => {
  const response = await api.post('/api/conversation/start', {
    receipt,
    people,
  });
  return response.data;
};

/**
 * Send a message in the conversation
 * @param {string} conversationId - Conversation ID
 * @param {string} message - User message
 * @returns {Promise<{message: string, assignment_state: Object, highlighted_items: string[]}>}
 */
export const sendMessage = async (conversationId, message) => {
  const response = await api.post(`/api/conversation/${conversationId}/message`, {
    message,
  });
  return response.data;
};

/**
 * Get current assignment state
 * @param {string} conversationId - Conversation ID
 * @returns {Promise<{assignment_state: Object, unassigned_items: Array, totals: Object}>}
 */
export const getAssignmentState = async (conversationId) => {
  const response = await api.get(`/api/conversation/${conversationId}/state`);
  return response.data;
};

/**
 * Get conversation messages
 * @param {string} conversationId - Conversation ID
 * @returns {Promise<{conversation_id: string, messages: Array}>}
 */
export const getMessages = async (conversationId) => {
  const response = await api.get(`/api/conversation/${conversationId}/messages`);
  return response.data;
};

/**
 * Confirm the split and finalize
 * @param {string} conversationId - Conversation ID
 * @returns {Promise<{conversation_id: string, status: string, totals: Object, message: string}>}
 */
export const confirmSplit = async (conversationId) => {
  const response = await api.post(`/api/conversation/${conversationId}/confirm`);
  return response.data;
};

export default api;
