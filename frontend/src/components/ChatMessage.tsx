import React from 'react';
import { Bot, User, MapPin, CloudOff, ShieldQuestion, Info } from 'lucide-react';
import { Message } from '../types';
import { AdvisoryCard } from './AdvisoryCard';
import { SeverityBadge } from './SeverityBadge';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const parsed = message.parsedAdvisory;

  const formattedTime = new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(new Date(message.timestamp));

  if (isUser) {
    return (
      <div
        id={`user-message-${message.id}`}
        className="flex justify-end mb-4 group animate-in fade-in slide-in-from-bottom-2 duration-200"
      >
        <div className="flex flex-col items-end max-w-[85%] sm:max-w-[75%]">
          <div className="flex items-center gap-1.5 mb-1 text-[11px] text-slate-400 font-medium">
            <span>You</span>
            <span>•</span>
            <span>{formattedTime}</span>
          </div>

          <div className="flex items-start gap-2 flex-row-reverse">
            <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center shrink-0 text-xs shadow-xs dark:bg-slate-700">
              <User size={14} />
            </div>

            <div className="px-4 py-2.5 rounded-2xl rounded-tr-sm bg-sky-600 text-white shadow-xs text-sm leading-relaxed">
              <p className="whitespace-pre-wrap">{message.text}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Bot Message
  return (
    <div
      id={`bot-message-${message.id}`}
      className="flex justify-start mb-5 group animate-in fade-in slide-in-from-bottom-2 duration-200"
    >
      <div className="flex flex-col items-start w-full max-w-[95%] sm:max-w-[85%]">
        <div className="flex items-center gap-1.5 mb-1.5 text-[11px] text-slate-400 font-medium">
          <span className="text-sky-600 dark:text-sky-400 font-semibold">Support Bot</span>
          <span>•</span>
          <span>{formattedTime}</span>
          {message.protocolId && !parsed?.isStructuredAdvisory && (
            <>
              <span>•</span>
              <span className="font-mono text-slate-500">SOP: {message.protocolId}</span>
            </>
          )}
          {message.severity && !parsed?.isStructuredAdvisory && (
            <SeverityBadge severity={message.severity} size="sm" />
          )}
        </div>

        <div className="flex items-start gap-2.5 w-full">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-xs mt-0.5">
            <Bot size={16} />
          </div>

          <div className="w-full min-w-0">
            {/* If structured advisory was recognized */}
            {parsed?.isStructuredAdvisory ? (
              <AdvisoryCard advisory={parsed} />
            ) : parsed?.fallbackType === 'missing_location' ? (
              /* Missing Location Fallback Card */
              <div
                id="fallback-missing-location"
                className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-slate-800 dark:bg-amber-950/30 dark:border-amber-900/50 dark:text-slate-200"
              >
                <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold text-amber-700 dark:text-amber-400">
                  <MapPin size={15} />
                  <span>Location Required</span>
                </div>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
              </div>
            ) : parsed?.fallbackType === 'weather_failure' ? (
              /* Weather Retrieval Failure Fallback Card */
              <div
                id="fallback-weather-failure"
                className="p-4 rounded-xl bg-rose-50/70 border border-rose-200 text-slate-800 dark:bg-rose-950/30 dark:border-rose-900/50 dark:text-slate-200"
              >
                <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold text-rose-700 dark:text-rose-400">
                  <CloudOff size={15} />
                  <span>Weather Data Unavailable</span>
                </div>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
              </div>
            ) : parsed?.fallbackType === 'no_sop' ? (
              /* No Matching SOP Fallback Card */
              <div
                id="fallback-no-sop"
                className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-slate-800 dark:bg-slate-800/60 dark:border-slate-700 dark:text-slate-200"
              >
                <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300">
                  <ShieldQuestion size={15} className="text-sky-500" />
                  <span>No Specific Policy Matched</span>
                </div>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
              </div>
            ) : (
              /* Normal conversational bot message */
              <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs text-slate-800 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200">
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
