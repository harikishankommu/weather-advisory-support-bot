import { ChatResponse } from '../types';

export const DEFAULT_API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || '';

const STORAGE_KEY_API_URL = 'weather_support_bot_api_url';

export function getStoredApiBaseUrl(): string {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_API_URL);

    if (saved && saved.trim()) {
      return saved.trim().replace(/\/+$/, '');
    }
  } catch {
    // Ignore storage errors
  }

  return DEFAULT_API_BASE_URL.replace(/\/+$/, '');
}

export function setStoredApiBaseUrl(url: string): void {
  try {
    localStorage.setItem(
      STORAGE_KEY_API_URL,
      url.trim().replace(/\/+$/, '')
    );
  } catch {
    // Ignore storage errors
  }
}

export async function sendMessage(
  message: string,
  sessionId: string,
  customBaseUrl?: string
): Promise<ChatResponse> {

  const baseUrl = customBaseUrl ?? getStoredApiBaseUrl();

  const endpoint = `${baseUrl}/chat`;

  const controller = new AbortController();

  const timeoutId = setTimeout(
    () => controller.abort(),
    20000
  );

  try {
    const response = await fetch(endpoint, {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),

      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');

      throw new Error(
        `Backend returned HTTP ${response.status}: ${
          errorText || response.statusText
        }`
      );
    }

    const data = await response.json();

    return {
      reply: data.reply ?? '',
      protocol_id: data.protocol_id ?? null,
      severity: data.severity ?? null,
    };

  } catch (err: any) {

    clearTimeout(timeoutId);

    if (err.name === 'AbortError') {
      throw new Error(
        'Connection timed out while waiting for backend.'
      );
    }

    throw err;
  }
}

export async function checkBackendHealth(
  customBaseUrl?: string
): Promise<{ status: string }> {

  const baseUrl =
    customBaseUrl ?? getStoredApiBaseUrl();

  const endpoint = `${baseUrl}/health`;

  const controller = new AbortController();

  const timeoutId = setTimeout(
    () => controller.abort(),
    5000
  );

  try {

    const response = await fetch(endpoint, {
      method: 'GET',

      headers: {
        Accept: 'application/json',
      },

      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(
        `Health check returned HTTP ${response.status}`
      );
    }

    return await response.json();

  } catch (err) {

    clearTimeout(timeoutId);

    throw err;
  }
}