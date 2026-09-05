import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  disabled = false,
}) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!text.trim() || isLoading || disabled) return;
    onSendMessage(text);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full bg-white/95 backdrop-blur-md border-t border-slate-200/90 p-3 sm:p-4 dark:bg-slate-900/95 dark:border-slate-800">
      <form
        onSubmit={handleSubmit}
        className="max-w-4xl mx-auto flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-2xl p-1.5 focus-within:ring-2 focus-within:ring-sky-500/30 focus-within:border-sky-500 transition-all shadow-2xs dark:bg-slate-800/80 dark:border-slate-700"
      >
        <textarea
          ref={textareaRef}
          id="chat-input-textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading || disabled}
          rows={1}
          placeholder={
            isLoading
              ? 'Analyzing advisory...'
              : 'Ask about cycling, running, picnics, walking the dog in your city...'
          }
          className="w-full resize-none bg-transparent px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-hidden disabled:opacity-50 dark:text-white dark:placeholder:text-slate-500 max-h-36 overflow-y-auto leading-relaxed"
        />

        <div className="flex items-center gap-1.5 shrink-0 pb-1 pr-1">
          <button
            id="send-message-button"
            type="submit"
            disabled={!text.trim() || isLoading || disabled}
            className="flex items-center justify-center w-9 h-9 rounded-xl bg-sky-600 text-white hover:bg-sky-700 disabled:opacity-30 disabled:hover:bg-sky-600 disabled:cursor-not-allowed transition-all shadow-xs"
            title="Send message (Enter)"
          >
            <Send size={16} className={isLoading ? 'opacity-0' : 'translate-x-0.5'} />
          </button>
        </div>
      </form>

      <div className="max-w-4xl mx-auto mt-2 px-2 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center gap-1">
          <CornerDownLeft size={11} /> Press <kbd className="font-mono bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-[10px]">Enter</kbd> to send, <kbd className="font-mono bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-[10px]">Shift+Enter</kbd> for newline
        </span>
        <span className="hidden sm:inline">Responses are governed by predefined SOP protocols</span>
      </div>
    </div>
  );
};
