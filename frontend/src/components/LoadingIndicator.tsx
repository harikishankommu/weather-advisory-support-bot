import React from 'react';
import { Bot, Loader2 } from 'lucide-react';

interface LoadingIndicatorProps {
  stageText: string;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ stageText }) => {
  return (
    <div
      id="chat-loading-indicator"
      className="flex justify-start mb-4 animate-in fade-in slide-in-from-bottom-2 duration-150"
    >
      <div className="flex items-start gap-2.5 max-w-[85%]">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-sky-500 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-xs mt-0.5">
          <Bot size={16} />
        </div>

        <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs text-slate-700 flex items-center gap-3 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-300">
          <Loader2 size={16} className="text-sky-600 animate-spin shrink-0 dark:text-sky-400" />
          <div className="flex flex-col">
            <span className="text-xs font-medium text-slate-800 dark:text-slate-200 transition-all duration-300">
              {stageText}
            </span>
            <span className="text-[10px] text-slate-400">
              Consulting live weather & safety guidelines
            </span>
          </div>
          <div className="flex gap-1 ml-2">
            <span className="w-1.5 h-1.5 rounded-full bg-sky-500 animate-bounce [animation-delay:-0.3s]" />
            <span className="w-1.5 h-1.5 rounded-full bg-sky-500 animate-bounce [animation-delay:-0.15s]" />
            <span className="w-1.5 h-1.5 rounded-full bg-sky-500 animate-bounce" />
          </div>
        </div>
      </div>
    </div>
  );
};
