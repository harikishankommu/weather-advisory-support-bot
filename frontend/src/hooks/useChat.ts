import { useState, useEffect, useCallback, useRef } from 'react';
import { Message, ParsedAdvisory } from '../types';
import {
  sendMessage as apiSendMessage,
  checkBackendHealth,
  getStoredApiBaseUrl,
  setStoredApiBaseUrl,
} from '../services/api';
import { parseAdvisory } from '../utils/parseAdvisory';

const SESSION_STORAGE_KEY = 'weather_support_bot_session_id';

function generateSessionId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `session_${Math.random().toString(36).substring(2, 11)}_${Date.now()}`;
}

export function useChat() {
  const [sessionId, setSessionId] = useState<string>(() => {
    try {
      const existing = sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (existing) return existing;
    } catch {
      // ignore
    }
    const fresh = generateSessionId();
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, fresh);
    } catch {
      // ignore
    }
    return fresh;
  });

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingStage, setLoadingStage] = useState<string>('Checking live weather...');
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [apiUrl, setApiUrl] = useState<string>(getStoredApiBaseUrl());
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const lastFailedMessageRef = useRef<string | null>(null);

  // Loading text cycler
  useEffect(() => {
    if (!isLoading) return;
    const stages = [
      'Checking live weather...',
      'Matching safety protocols...',
      'Generating grounded advisory...',
    ];
    let currentIndex = 0;
    const interval = setInterval(() => {
      currentIndex = (currentIndex + 1) % stages.length;
      setLoadingStage(stages[currentIndex]);
    }, 1800);

    return () => clearInterval(interval);
  }, [isLoading]);

  // Periodic health check on mount or when API URL changes
  const verifyHealth = useCallback(async (customUrl?: string) => {
    const urlToTest = customUrl || apiUrl;
    try {
      await checkBackendHealth(urlToTest);
      setIsBackendHealthy(true);
    } catch {
      setIsBackendHealthy(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    verifyHealth();
  }, [verifyHealth]);

  const handleUpdateApiUrl = useCallback((newUrl: string) => {
    setStoredApiBaseUrl(newUrl);
    setApiUrl(newUrl);
    verifyHealth(newUrl);
  }, [verifyHealth]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setConnectionError(null);
    lastFailedMessageRef.current = null;
    const freshId = generateSessionId();
    setSessionId(freshId);
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, freshId);
    } catch {
      // ignore
    }
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      setConnectionError(null);
      lastFailedMessageRef.current = trimmed;

      const userMessage: Message = {
        id: `usr_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
        sender: 'user',
        text: trimmed,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setLoadingStage('Checking live weather...');

      try {
        const response = await apiSendMessage(trimmed, sessionId, apiUrl);
        
        const parsed: ParsedAdvisory = parseAdvisory(
          response.reply,
          response.protocol_id,
          response.severity
        );

        const botMessage: Message = {
          id: `bot_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
          sender: 'bot',
          text: response.reply,
          protocolId: response.protocol_id,
          severity: response.severity,
          parsedAdvisory: parsed,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, botMessage]);
        setIsBackendHealthy(true);
        lastFailedMessageRef.current = null;
      } catch (err: any) {
        setIsBackendHealthy(false);
        const errorMsg =
          'Unable to connect to the Weather Advisory backend. Please make sure the FastAPI server is running.';
        setConnectionError(errorMsg);
      } finally {
        setIsLoading(false);
      }
    },
    [apiUrl, isLoading, sessionId]
  );

  const retryLastMessage = useCallback(() => {
    if (lastFailedMessageRef.current) {
      sendMessage(lastFailedMessageRef.current);
    } else {
      verifyHealth();
    }
  }, [sendMessage, verifyHealth]);

  return {
    sessionId,
    messages,
    isLoading,
    loadingStage,
    connectionError,
    apiUrl,
    isBackendHealthy,
    sendMessage,
    clearChat,
    retryLastMessage,
    updateApiUrl: handleUpdateApiUrl,
    verifyHealth,
  };
}
