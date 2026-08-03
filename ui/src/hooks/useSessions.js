import { useState, useEffect, useCallback } from 'react';
import { fetchSessions, createSession as apiCreateSession, deleteSession as apiDeleteSession } from '../utils/api';

export function useSessions() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadSessions = useCallback(async () => {
    try {
      const data = await fetchSessions();
      setSessions(data || []);
      if (data && data.length > 0 && !activeSessionId) {
        setActiveSessionId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load sessions:', err);
    } finally {
      setIsLoading(false);
    }
  }, [activeSessionId]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const createSession = useCallback(async (provider, model) => {
    try {
      const newSession = await apiCreateSession(provider, model);
      setSessions(prev => [newSession, ...prev]);
      setActiveSessionId(newSession.id);
      return newSession;
    } catch (err) {
      console.error('Failed to create session:', err);
      throw err;
    }
  }, []);

  const deleteSession = useCallback(async (id) => {
    try {
      await apiDeleteSession(id);
      setSessions(prev => prev.filter(s => s.id !== id));
      if (activeSessionId === id) {
        setActiveSessionId(null);
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  }, [activeSessionId]);

  const activeSession = sessions.find(s => s.id === activeSessionId) || null;

  return {
    sessions,
    activeSessionId,
    activeSession,
    setActiveSessionId,
    createSession,
    deleteSession,
    isLoading
  };
}
