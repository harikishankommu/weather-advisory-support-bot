import React, { useState } from 'react';
import { MapPin, Clock, FileCode, CheckCircle2, Copy, Check, Code } from 'lucide-react';
import { ParsedAdvisory } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { WeatherDetails } from './WeatherDetails';

interface AdvisoryCardProps {
  advisory: ParsedAdvisory;
}

export const AdvisoryCard: React.FC<AdvisoryCardProps> = ({ advisory }) => {
  const [showRaw, setShowRaw] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyRaw = () => {
    navigator.clipboard.writeText(advisory.rawText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      id="advisory-card"
      className="w-full rounded-xl bg-white border border-slate-200 shadow-sm overflow-hidden text-slate-900 transition-all dark:bg-slate-900 dark:border-slate-800 dark:text-slate-100"
    >
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 bg-slate-50/80 border-b border-slate-200/80 dark:bg-slate-800/60 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
          <h3 className="font-semibold text-sm tracking-tight text-slate-900 dark:text-white">
            Weather Advisory
          </h3>
          {advisory.protocolId && (
            <span
              id="advisory-protocol-id"
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono font-medium bg-sky-100/70 text-sky-800 border border-sky-200/70 dark:bg-sky-950/60 dark:text-sky-300 dark:border-sky-800/80"
            >
              <FileCode size={12} />
              SOP: {advisory.protocolId}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {advisory.severity && <SeverityBadge severity={advisory.severity} size="sm" />}

          <button
            type="button"
            onClick={() => setShowRaw(!showRaw)}
            title="Toggle raw response"
            className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors dark:hover:text-slate-200 dark:hover:bg-slate-800 text-xs flex items-center gap-1 font-mono"
          >
            <Code size={13} />
            <span className="hidden sm:inline">{showRaw ? 'Formatted' : 'Raw'}</span>
          </button>
        </div>
      </div>

      {showRaw ? (
        /* Raw response view for fidelity */
        <div className="p-4 bg-slate-950 text-slate-200 font-mono text-xs whitespace-pre-wrap leading-relaxed relative rounded-b-xl overflow-x-auto">
          <button
            type="button"
            onClick={handleCopyRaw}
            className="absolute top-3 right-3 p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors flex items-center gap-1 text-[11px]"
          >
            {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
          {advisory.rawText}
        </div>
      ) : (
        /* Formatted visual advisory */
        <div className="p-4 space-y-3.5">
          {/* Metadata badges: Location and Time */}
          {(advisory.location || advisory.time) && (
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 dark:text-slate-300">
              {advisory.location && (
                <div
                  id="advisory-location"
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 font-medium dark:bg-slate-800/70 dark:border-slate-700"
                >
                  <MapPin size={13} className="text-rose-500 shrink-0" />
                  <span className="text-slate-400 text-[11px] font-normal">Location:</span>
                  <span className="text-slate-900 font-semibold dark:text-white capitalize">
                    {advisory.location}
                  </span>
                </div>
              )}

              {advisory.time && (
                <div
                  id="advisory-time"
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 font-medium dark:bg-slate-800/70 dark:border-slate-700"
                >
                  <Clock size={13} className="text-sky-500 shrink-0" />
                  <span className="text-slate-400 text-[11px] font-normal">Time:</span>
                  <span className="text-slate-900 font-semibold dark:text-white capitalize">
                    {advisory.time}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Weather Conditions metrics */}
          {advisory.weatherConditions && (
            <WeatherDetails conditions={advisory.weatherConditions} />
          )}

          {/* Guidance Section */}
          {advisory.guidance && (
            <div
              id="advisory-guidance"
              className="p-3.5 rounded-lg bg-sky-50/60 border border-sky-100 text-sky-950 dark:bg-sky-950/30 dark:border-sky-900/50 dark:text-sky-100"
            >
              <div className="flex items-center gap-1.5 mb-1.5 text-xs font-semibold uppercase tracking-wider text-sky-700 dark:text-sky-300">
                <CheckCircle2 size={14} className="text-sky-600 dark:text-sky-400" />
                <span>Safety Guidance</span>
              </div>
              <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-200 font-normal">
                {advisory.guidance}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
