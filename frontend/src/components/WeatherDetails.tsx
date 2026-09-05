import React from 'react';
import { Thermometer, Wind, CloudRain, Umbrella, Sun, Gauge } from 'lucide-react';
import { WeatherConditionMetrics } from '../types';

interface WeatherDetailsProps {
  conditions: WeatherConditionMetrics;
}

export const WeatherDetails: React.FC<WeatherDetailsProps> = ({ conditions }) => {
  const { temperature, windSpeed, precipitation, precipitationProbability, uvIndex } = conditions;

  const hasAnyMetric =
    temperature || windSpeed || precipitation || precipitationProbability || uvIndex;

  if (!hasAnyMetric) {
    return null;
  }

  return (
    <div id="weather-details-container" className="my-3">
      <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        <Gauge size={13} className="text-sky-500" />
        <span>Weather Conditions</span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {temperature && (
          <div
            id="weather-metric-temp"
            className="flex items-center gap-2.5 p-2.5 rounded-lg bg-slate-50/80 border border-slate-200/80 text-slate-800 dark:bg-slate-900/60 dark:border-slate-800 dark:text-slate-200"
          >
            <div className="p-1.5 rounded-md bg-amber-50 text-amber-600 border border-amber-200/60 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-900/50">
              <Thermometer size={16} />
            </div>
            <div className="min-w-0">
              <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">
                Temperature
              </div>
              <div className="text-sm font-semibold truncate text-slate-900 dark:text-white">
                {temperature}
              </div>
            </div>
          </div>
        )}

        {windSpeed && (
          <div
            id="weather-metric-wind"
            className="flex items-center gap-2.5 p-2.5 rounded-lg bg-slate-50/80 border border-slate-200/80 text-slate-800 dark:bg-slate-900/60 dark:border-slate-800 dark:text-slate-200"
          >
            <div className="p-1.5 rounded-md bg-cyan-50 text-cyan-600 border border-cyan-200/60 dark:bg-cyan-950/40 dark:text-cyan-400 dark:border-cyan-900/50">
              <Wind size={16} />
            </div>
            <div className="min-w-0">
              <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">
                Wind Speed
              </div>
              <div className="text-sm font-semibold truncate text-slate-900 dark:text-white">
                {windSpeed}
              </div>
            </div>
          </div>
        )}

        {precipitation && (
          <div
            id="weather-metric-precip"
            className="flex items-center gap-2.5 p-2.5 rounded-lg bg-slate-50/80 border border-slate-200/80 text-slate-800 dark:bg-slate-900/60 dark:border-slate-800 dark:text-slate-200"
          >
            <div className="p-1.5 rounded-md bg-blue-50 text-blue-600 border border-blue-200/60 dark:bg-blue-950/40 dark:text-blue-400 dark:border-blue-900/50">
              <CloudRain size={16} />
            </div>
            <div className="min-w-0">
              <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">
                Precipitation
              </div>
              <div className="text-sm font-semibold truncate text-slate-900 dark:text-white">
                {precipitation}
              </div>
            </div>
          </div>
        )}

        {precipitationProbability && (
          <div
            id="weather-metric-precip-prob"
            className="flex items-center gap-2.5 p-2.5 rounded-lg bg-slate-50/80 border border-slate-200/80 text-slate-800 dark:bg-slate-900/60 dark:border-slate-800 dark:text-slate-200"
          >
            <div className="p-1.5 rounded-md bg-indigo-50 text-indigo-600 border border-indigo-200/60 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-900/50">
              <Umbrella size={16} />
            </div>
            <div className="min-w-0">
              <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">
                Rain Prob.
              </div>
              <div className="text-sm font-semibold truncate text-slate-900 dark:text-white">
                {precipitationProbability}
              </div>
            </div>
          </div>
        )}

        {uvIndex && (
          <div
            id="weather-metric-uv"
            className="flex items-center gap-2.5 p-2.5 rounded-lg bg-slate-50/80 border border-slate-200/80 text-slate-800 dark:bg-slate-900/60 dark:border-slate-800 dark:text-slate-200"
          >
            <div className="p-1.5 rounded-md bg-violet-50 text-violet-600 border border-violet-200/60 dark:bg-violet-950/40 dark:text-violet-400 dark:border-violet-900/50">
              <Sun size={16} />
            </div>
            <div className="min-w-0">
              <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">
                UV Index
              </div>
              <div className="text-sm font-semibold truncate text-slate-900 dark:text-white">
                {uvIndex}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
