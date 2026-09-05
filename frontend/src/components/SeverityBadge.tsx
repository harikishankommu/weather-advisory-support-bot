import React from 'react';
import { Shield, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';
import { SeverityLevel } from '../types';

interface SeverityBadgeProps {
  severity?: SeverityLevel | null;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  severity,
  className = '',
  size = 'md',
}) => {
  if (!severity) return null;

  const normalized = severity.trim().toLowerCase();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-300 dark:bg-slate-800 dark:text-slate-300';
  let Icon = Shield;
  let label = severity.toUpperCase();

  if (normalized === 'low') {
    colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-xs dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800';
    Icon = ShieldCheck;
  } else if (normalized === 'medium') {
    colorClasses = 'bg-amber-50 text-amber-700 border-amber-200 shadow-xs dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800';
    Icon = AlertTriangle;
  } else if (normalized === 'high') {
    colorClasses = 'bg-orange-50 text-orange-700 border-orange-200 shadow-xs dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-800';
    Icon = ShieldAlert;
  } else if (normalized === 'critical') {
    colorClasses = 'bg-rose-50 text-rose-700 border-rose-200 shadow-xs dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800';
    Icon = ShieldAlert;
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs font-semibold px-2.5 py-1 gap-1.5',
    lg: 'text-sm font-semibold px-3 py-1.5 gap-2',
  }[size];

  const iconSizes = {
    sm: 12,
    md: 14,
    lg: 16,
  }[size];

  return (
    <span
      id={`severity-badge-${normalized}`}
      className={`inline-flex items-center rounded-md border tracking-wider font-mono uppercase transition-colors ${sizeClasses} ${colorClasses} ${className}`}
    >
      <Icon size={iconSizes} className="shrink-0" />
      <span>{label}</span>
    </span>
  );
};
