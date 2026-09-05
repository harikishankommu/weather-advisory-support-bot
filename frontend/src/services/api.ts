import { ChatResponse } from '../types';

const DEFAULT_API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || '';

const STORAGE_KEY_API_URL =
  'weather_support_bot_api_url';


function normalizeBaseUrl(url: string): string {
  return url.trim().replace(/\/+$/, '');
}


export function getStoredApiBaseUrl(): string {
  try {
    const saved = localStorage.getItem(
      STORAGE_KEY_API_URL
    );

    if (saved && saved.trim()) {
      return normalizeBaseUrl(saved);
    }
  } catch {
    // Ignore storage errors
  }

  return normalizeBaseUrl(
    DEFAULT_API_BASE_URL
  );
}


export function setStoredApiBaseUrl(
  url: string
): void {
  try {
    localStorage.setItem(
      STORAGE_KEY_API_URL,
      normalizeBaseUrl(url)
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

  const baseUrl =
    customBaseUrl !== undefined
      ? normalizeBaseUrl(customBaseUrl)
      : getStoredApiBaseUrl();

  const endpoint =
    `${baseUrl}/chat`;

  const controller =
    new AbortController();

  const timeoutId =
    setTimeout(
      () => controller.abort(),
      20000
    );

  try {

    const response = await fetch(
      endpoint,
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json',
        },

        body: JSON.stringify({
          message,
          session_id: sessionId,
        }),

        signal: controller.signal,
      }
    );

    if (!response.ok) {

      const errorText =
        await response.text()
          .catch(() => '');

      throw new Error(
        `Backend returned HTTP ${response.status}: ${
          errorText ||
          response.statusText
        }`
      );
    }

    const data =
      await response.json();

    return {
      reply: data.reply ?? '',
      protocol_id:
        data.protocol_id ?? null,
      severity:
        data.severity ?? null,
    };

  } catch (err: any) {

    if (
      err?.name === 'AbortError'
    ) {
      throw new Error(
        'Connection timed out while waiting for backend.'
      );
    }

    throw err;

  } finally {

    clearTimeout(
      timeoutId
    );

  }
}


export async function checkBackendHealth(
  customBaseUrl?: string
): Promise<{ status: string }> {

  const baseUrl =
    customBaseUrl !== undefined
      ? normalizeBaseUrl(customBaseUrl)
      : getStoredApiBaseUrl();

  const endpoint =
    `${baseUrl}/health`;

  const controller =
    new AbortController();

  const timeoutId =
    setTimeout(
      () => controller.abort(),
      5000
    );

  try {

    const response =
      await fetch(
        endpoint,
        {
          method: 'GET',

          headers: {
            Accept:
              'application/json',
          },

          signal:
            controller.signal,
        }
      );

    if (!response.ok) {

      throw new Error(
        `Health check returned HTTP ${response.status}`
      );

    }

    return await response.json();

  } catch (err: any) {

    if (
      err?.name === 'AbortError'
    ) {
      throw new Error(
        'Backend health check timed out.'
      );
    }

    throw err;

  } finally {

    clearTimeout(
      timeoutId
    );

  }
}