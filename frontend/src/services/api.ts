import { ChatResponse } from '../types';

export const DEFAULT_API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || '';

const STORAGE_KEY_API_URL = 'weather_support_bot_api_url';

function normalizeBaseUrl(url: string): string {
  return url.trim().replace(/\/+$/, '');
}

export function getStoredApiBaseUrl(): string {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_API_URL);

    if (saved && saved.trim()) {
      const normalized = normalizeBaseUrl(saved);

      // Ignore old localhost URLs in production.
      if (
        normalized.includes('127.0.0.1') ||
        normalized.includes('localhost')
      ) {
        return normalizeBaseUrl(DEFAULT_API_BASE_URL);
      }

      return normalized;
    }
  } catch {
    // Ignore storage errors.
  }

  return normalizeBaseUrl(DEFAULT_API_BASE_URL);
}

export function setStoredApiBaseUrl(url: string): void {
  try {
    const normalized = normalizeBaseUrl(url);

    // Do not save localhost as the production backend.
    if (
      normalized.includes('127.0.0.1') ||
      normalized.includes('localhost')
    ) {
      localStorage.removeItem(STORAGE_KEY_API_URL);
      return;
    }

    localStorage.setItem(
      STORAGE_KEY_API_URL,
      normalized
    );
  } catch {
    // Ignore storage errors.
  }
}

export function clearStoredApiBaseUrl(): void {
  try {
    localStorage.removeItem(STORAGE_KEY_API_URL);
  } catch {
    // Ignore storage errors.
  }
}

export async function sendMessage(
  message: string,
  sessionId: string,
  customBaseUrl?: string
): Promise<ChatResponse> {
  const baseUrl =
    customBaseUrl ??
    getStoredApiBaseUrl();

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

    if (!response.ok) {
      const errorText =
        await response.text().catch(() => '');

      throw new Error(
        `Backend returned HTTP ${response.status}: ${
          errorText || response.statusText
        }`
      );
    }

    const data = await response.json();

    return {
      reply: data.reply ?? '',
      protocol_id:
        data.protocol_id ?? null,
      severity:
        data.severity ?? null,
    };

  } catch (err: any) {
    if (err?.name === 'AbortError') {
      throw new Error(
        'Connection timed out while waiting for backend.'
      );
    }

    throw err;

  } finally {
    clearTimeout(timeoutId);
  }
}

export async function checkBackendHealth(
  customBaseUrl?: string
): Promise<{ status: string }> {
  const baseUrl =
    customBaseUrl ??
    getStoredApiBaseUrl();

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

    if (!response.ok) {
      throw new Error(
        `Health check returned HTTP ${response.status}`
      );
    }

    return await response.json();

  } finally {
    clearTimeout(timeoutId);
  }
}