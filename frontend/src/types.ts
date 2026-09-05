export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical' | string;

export interface WeatherConditionMetrics {
  temperature?: string;
  windSpeed?: string;
  precipitation?: string;
  precipitationProbability?: string;
  uvIndex?: string;
  rawItems?: string[];
}

export type FallbackType = 'missing_location' | 'weather_failure' | 'no_sop' | 'standard';

export interface ParsedAdvisory {
  isStructuredAdvisory: boolean;
  title?: string;
  location?: string;
  time?: string;
  protocolId?: string;
  severity?: SeverityLevel;
  weatherConditions?: WeatherConditionMetrics;
  guidance?: string;
  rawText: string;
  fallbackType?: FallbackType;
}

export interface ChatResponse {
  reply: string;
  protocol_id?: string | null;
  severity?: string | null;
}

export interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: Date;
  protocolId?: string | null;
  severity?: string | null;
  parsedAdvisory?: ParsedAdvisory;
  isError?: boolean;
}

export interface BackendHealthStatus {
  isOnline: boolean | null;
  lastChecked?: Date;
  error?: string;
}
