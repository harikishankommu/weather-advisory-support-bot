import React from 'react';
import { Compass, Sparkles, ArrowRight, Shield, CloudSun } from 'lucide-react';

interface WelcomeScreenProps {
  onSelectPrompt: (prompt: string) => void;
}

const EXAMPLE_PROMPTS = [
  'Is it safe to go cycling in Hyderabad today?',
  'Can I go running in Mumbai tomorrow?',
  'Is today good for a picnic in Delhi?',
  'Is it safe to take my dog for a walk in Chennai?',
  'Can my grandmother go outside in Hyderabad tomorrow?',
];

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSelectPrompt }) => {
  return (
    <div
      id="welcome-screen"
      className="flex flex-col items-center justify-center min-h-[60vh] max-w-2xl mx-auto px-4 py-8 text-center"
    >
      {/* Visual Badge */}
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sky-50 border border-sky-200/80 text-sky-700 text-xs font-medium mb-5 dark:bg-sky-950/50 dark:border-sky-800 dark:text-sky-300">
        <CloudSun size={15} className="text-sky-500" />
        <span>Grounded Policy & Real-time Weather Intelligence</span>
      </div>

      <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white mb-3">
        How can I help you plan safely?
      </h2>

      <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 max-w-xl mb-8 leading-relaxed">
        Ask about outdoor activities, travel, or weather-related situations. The system checks live weather conditions and matches your situation against predefined safety protocols.
      </p>

      {/* Suggested prompts list */}
      <div className="w-full text-left space-y-2.5">
        <div className="flex items-center justify-between px-1 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Sparkles size={13} className="text-amber-500" />
            Try an example scenario
          </span>
          <span className="text-xs text-slate-400">Click to run</span>
        </div>

        <div className="grid grid-cols-1 gap-2">
          {EXAMPLE_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              id={`example-prompt-${idx}`}
              type="button"
              onClick={() => onSelectPrompt(prompt)}
              className="group flex items-center justify-between w-full p-3 rounded-xl bg-white border border-slate-200/90 hover:border-sky-400 hover:bg-sky-50/40 text-left transition-all duration-150 shadow-2xs hover:shadow-xs dark:bg-slate-900 dark:border-slate-800 dark:hover:border-sky-600 dark:hover:bg-slate-800/60"
            >
              <div className="flex items-center gap-3 pr-2">
                <span className="w-6 h-6 rounded-lg bg-slate-100 group-hover:bg-sky-100 text-slate-500 group-hover:text-sky-600 flex items-center justify-center text-xs font-mono shrink-0 transition-colors dark:bg-slate-800 dark:group-hover:bg-sky-950 dark:group-hover:text-sky-300">
                  {idx + 1}
                </span>
                <span className="text-sm text-slate-700 group-hover:text-slate-900 font-medium dark:text-slate-300 dark:group-hover:text-white">
                  {prompt}
                </span>
              </div>
              <ArrowRight
                size={16}
                className="text-slate-300 group-hover:text-sky-600 group-hover:translate-x-0.5 transition-all shrink-0 dark:text-slate-600 dark:group-hover:text-sky-400"
              />
            </button>
          ))}
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-slate-200/80 w-full flex items-center justify-center gap-4 text-xs text-slate-400 dark:border-slate-800">
        <span className="flex items-center gap-1">
          <Shield size={13} className="text-emerald-500" /> Policy-driven safety
        </span>
        <span>•</span>
        <span className="flex items-center gap-1">
          <Compass size={13} className="text-sky-500" /> Time-aware context
        </span>
      </div>
    </div>
  );
};
