import React, { useState } from 'react';
import { Trash2, Radio, Server, Check, Edit2, ShieldAlert } from 'lucide-react';

interface HeaderProps {
  sessionId: string;
  isBackendHealthy: boolean | null;
  apiUrl: string;
  onClearChat: () => void;
  onUpdateApiUrl: (newUrl: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  sessionId,
  isBackendHealthy,
  apiUrl,
  onClearChat,
  onUpdateApiUrl,
}) => {
  const [showConfig, setShowConfig] = useState(false);
  const [tempUrl, setTempUrl] = useState(apiUrl);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (tempUrl.trim()) {
      onUpdateApiUrl(tempUrl.trim());
      setShowConfig(false);
    }
  };

  const shortSession = sessionId.length > 16 
    ? `${sessionId.substring(0, 8)}...${sessionId.substring(sessionId.length - 4)}` 
    : sessionId;

  return (
    <header
      id="app-header"
      className="sticky top-0 z-30 w-full bg-slate-900 text-white border-b border-slate-800 shadow-md backdrop-blur-md"
    >
      <div className="max-w-5xl mx-auto px-4 py-3 sm:py-3.5 flex items-center justify-between gap-4">
        {/* Branding & Subtitle */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-500 p-0.5 shadow-xs shrink-0 flex items-center justify-center text-xl select-none">
            🌦️
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="font-semibold text-base sm:text-lg tracking-tight truncate text-white">
                Weather Advisory Support Bot
              </h1>
            </div>
            <p className="text-xs text-slate-300 sm:text-[13px] truncate">
              Live weather insights combined with policy-driven safety guidance.
            </p>
          </div>
        </div>

        {/* Controls & Badges */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          {/* Backend Health Status Badge */}
          <div
            id="backend-health-status"
            className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 border border-slate-700 text-slate-300"
            title={`Connected to ${apiUrl}`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isBackendHealthy === true
                  ? 'bg-emerald-400 animate-pulse'
                  : isBackendHealthy === false
                  ? 'bg-rose-500'
                  : 'bg-amber-400 animate-pulse'
              }`}
            />
            <span className="text-[11px] font-mono">
              {isBackendHealthy === true
                ? 'Backend Online'
                : isBackendHealthy === false
                ? 'Backend Offline'
                : 'Connecting...'}
            </span>
          </div>

          {/* Session ID indicator */}
          <div
            id="session-id-badge"
            className="hidden md:inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono bg-slate-800/80 border border-slate-700/60 text-slate-400"
            title={`Active Session: ${sessionId}`}
          >
            <Radio size={11} className="text-sky-400 shrink-0" />
            <span>{shortSession}</span>
          </div>

          {/* Server endpoint toggle */}
          <button
            type="button"
            onClick={() => setShowConfig(!showConfig)}
            title="Configure FastAPI endpoint"
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition-colors"
          >
            <Server size={15} />
          </button>

          {/* Clear Chat button */}
          <button
            id="clear-chat-button"
            type="button"
            onClick={onClearChat}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-rose-950/80 hover:text-rose-300 hover:border-rose-800 border border-slate-700 text-slate-200 text-xs font-medium transition-colors shadow-2xs"
            title="Clear conversation and reset session ID"
          >
            <Trash2 size={13} className="shrink-0" />
            <span className="hidden sm:inline">Clear Chat</span>
          </button>
        </div>
      </div>

      {/* Endpoint Configuration Bar */}
      {showConfig && (
        <div className="bg-slate-950 border-t border-slate-800 px-4 py-2.5 animate-in slide-in-from-top-1 duration-150">
          <div className="max-w-5xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="text-xs text-slate-300 flex items-center gap-1.5">
              <Server size={13} className="text-sky-400" />
              <span>FastAPI Backend Target:</span>
              <code className="text-sky-300 font-mono text-[11px]">{apiUrl}</code>
            </div>

            <form onSubmit={handleSave} className="flex items-center gap-2">
              <input
                type="text"
                value={tempUrl}
                onChange={(e) => setTempUrl(e.target.value)}
                placeholder="http://127.0.0.1:8000"
                className="px-2.5 py-1 text-xs font-mono rounded bg-slate-900 border border-slate-700 text-white w-56 focus:outline-hidden focus:border-sky-500"
              />
              <button
                type="submit"
                className="px-2.5 py-1 text-xs rounded bg-sky-600 hover:bg-sky-500 text-white font-medium flex items-center gap-1"
              >
                <Check size={12} />
                <span>Save</span>
              </button>
              <button
                type="button"
                onClick={() => {
                  setTempUrl('http://127.0.0.1:8000');
                  onUpdateApiUrl('http://127.0.0.1:8000');
                  setShowConfig(false);
                }}
                className="px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
              >
                Reset Default
              </button>
            </form>
          </div>
        </div>
      )}
    </header>
  );
};
