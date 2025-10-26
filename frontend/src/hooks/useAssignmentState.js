/**
 * Hook for managing assignment state with polling
 */
import { useState, useEffect, useCallback } from 'react';
import { getAssignmentState } from '../utils/api';

export const useAssignmentState = (conversationId, pollingInterval = 2000) => {
  const [assignmentState, setAssignmentState] = useState(null);
  const [unassignedItems, setUnassignedItems] = useState([]);
  const [totals, setTotals] = useState({});
  const [highlightedItems, setHighlightedItems] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Fetch assignment state from the server
   */
  const refresh = useCallback(async () => {
    if (!conversationId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await getAssignmentState(conversationId);
      setAssignmentState(data.assignment_state);
      setUnassignedItems(data.unassigned_items || []);
      setTotals(data.totals || {});
    } catch (err) {
      setError(err.message || 'Failed to load assignment state');
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  /**
   * Set up polling for assignment state updates
   */
  useEffect(() => {
    if (!conversationId) return;

    // Initial fetch
    refresh();

    // Set up polling
    const interval = setInterval(refresh, pollingInterval);

    return () => clearInterval(interval);
  }, [conversationId, pollingInterval, refresh]);

  return {
    assignmentState,
    unassignedItems,
    totals,
    highlightedItems,
    setHighlightedItems,
    refresh,
    isLoading,
    error,
  };
};
