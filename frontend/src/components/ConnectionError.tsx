import React, { useState } from 'react';
import { AlertCircle, RefreshCw, Terminal, Settings2, Check } from 'lucide-react';

interface ConnectionErrorProps {
  apiUrl: string;
  onRetry: () => void;
  onUpdateApiUrl?: (newUrl: string) => void;
}

export const ConnectionError: React.FC<ConnectionErrorProps> = ({
  apiUrl,
  onRetry,
  onUpdateApiUrl,
}) => {
  const [showConfig, setShowConfig] = useState(false);
  const [customUrl, setCustomUrl] = useState(apiUrl);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetryClick = async () => {
    setIsRetrying(true);
    try {
      await onRetry();
    } finally {
      setTimeout(() => setIsRetrying(false), 500);
    }
  };

  const handleSaveUrl = (e: React.FormEvent) => {
    e.preventDefault();
    if (onUpdateApiUrl && customUrl.trim()) {
      onUpdateApiUrl(customUrl.trim());
      setShowConfig(false);
    }
  };

  return (
    <div
      id="backend-connection-error"
      className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-950 mb-4 shadow-xs dark:bg-rose-950/40 dark:border-rose-900/60 dark:text-rose-100 animate-in fade-in duration-200"
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-rose-100 text-rose-600 dark:bg-rose-900 dark:text-rose-300 shrink-0">
          <AlertCircle size={20} />
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-sm text-rose-900 dark:text-rose-200 mb-1">
            Backend Connection Notice
          </h4>
          <p className="text-sm text-rose-800 dark:text-rose-300 leading-relaxed">
            Unable to connect to the Weather Advisory backend. Please make sure the FastAPI server is running.
          </p>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button
              id="retry-connection-button"
              type="button"
              onClick={handleRetryClick}
              disabled={isRetrying}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-medium shadow-xs transition-colors disabled:opacity-50"
            >
              <RefreshCw size={13} className={isRetrying ? 'animate-spin' : ''} />
              <span>{isRetrying ? 'Retrying...' : 'Retry Connection'}</span>
            </button>

            <button
              type="button"
              onClick={() => setShowConfig(!showConfig)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-100 hover:bg-rose-200 text-rose-900 text-xs font-medium transition-colors dark:bg-rose-900/50 dark:hover:bg-rose-900 dark:text-rose-200"
            >
              <Settings2 size={13} />
              <span>Configure Target URL ({apiUrl})</span>
            </button>
          </div>

          {showConfig && (
            <form
              onSubmit={handleSaveUrl}
              className="mt-3 p-3 rounded-lg bg-white/80 border border-rose-200/80 dark:bg-slate-900 dark:border-rose-900/60"
            >
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                FastAPI Backend URL:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={customUrl}
                  onChange={(e) => setCustomUrl(e.target.value)}
                  placeholder="http://127.0.0.1:8000"
                  className="flex-1 px-3 py-1.5 text-xs font-mono rounded-md border border-slate-300 bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
                />
                <button
                  type="submit"
                  className="px-3 py-1.5 rounded-md bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium dark:bg-slate-700 dark:hover:bg-slate-600 flex items-center gap-1"
                >
                  <Check size={13} />
                  <span>Apply</span>
                </button>
              </div>
            </form>
          )}

          <div className="mt-3 pt-2.5 border-t border-rose-200/60 dark:border-rose-900/50 text-[11px] text-rose-700 dark:text-rose-400 flex items-center gap-1.5 font-mono">
            <Terminal size={12} className="shrink-0" />
             <span>uvicorn backend.main:app --reload --port 8000</span>
          </div>
        </div>
      </div>
    </div>
  );
};
