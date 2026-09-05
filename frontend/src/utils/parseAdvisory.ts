import { ParsedAdvisory, WeatherConditionMetrics, FallbackType } from '../types';

export function parseAdvisory(
  reply: string,
  apiProtocolId?: string | null,
  apiSeverity?: string | null
): ParsedAdvisory {
  const rawText = reply.trim();

  // Check fallback triggers based on standard backend responses
  let fallbackType: FallbackType = 'standard';
  const lowerText = rawText.toLowerCase();

  if (
    lowerText.includes('need a location') ||
    lowerText.includes('tell me the city or location') ||
    lowerText.includes('please provide a location')
  ) {
    fallbackType = 'missing_location';
  } else if (
    lowerText.includes("couldn't retrieve live weather data") ||
    lowerText.includes('unable to retrieve live weather') ||
    lowerText.includes('cannot retrieve live weather')
  ) {
    fallbackType = 'weather_failure';
  } else if (
    lowerText.includes("don't have a specific sop") ||
    lowerText.includes('no matching sop') ||
    lowerText.includes("i don't have a specific sop that applies")
  ) {
    fallbackType = 'no_sop';
  }

  // Detect if it is formatted as a structured Weather Advisory
  const hasAdvisoryHeader = /weather\s+advisory/i.test(rawText);
  const hasWeatherConditions = /weather\s+conditions:/i.test(rawText);
  const hasGuidance = /guidance:/i.test(rawText);

  const isStructuredAdvisory = hasAdvisoryHeader || (hasWeatherConditions && hasGuidance);

  if (!isStructuredAdvisory) {
    return {
      isStructuredAdvisory: false,
      rawText,
      fallbackType,
      protocolId: apiProtocolId || undefined,
      severity: apiSeverity || undefined,
    };
  }

  // Extract location
  const locationMatch = rawText.match(/Location:\s*([^\n\r]+)/i);
  const location = locationMatch ? locationMatch[1].trim() : undefined;

  // Extract time
  const timeMatch = rawText.match(/Time:\s*([^\n\r]+)/i);
  const time = timeMatch ? timeMatch[1].trim() : undefined;

  // Extract SOP
  const sopMatch = rawText.match(/(?:Selected SOP|SOP|Protocol):\s*([^\n\r]+)/i);
  const protocolId = apiProtocolId || (sopMatch ? sopMatch[1].trim() : undefined);

  // Extract Severity
  const severityMatch = rawText.match(/Severity:\s*([^\n\r]+)/i);
  const severity = apiSeverity || (severityMatch ? severityMatch[1].trim() : undefined);

  // Extract Weather conditions section
  const weatherSectionMatch = rawText.match(
    /Weather\s+conditions:\s*([\s\S]*?)(?=(?:\n\s*Guidance:|$))/i
  );
  
  const weatherConditions: WeatherConditionMetrics = {};
  if (weatherSectionMatch && weatherSectionMatch[1]) {
    const sectionText = weatherSectionMatch[1];
    
    // Temperature: 31.8 °C
    const tempMatch = sectionText.match(/Temperature:\s*([^\n\r]+)/i);
    if (tempMatch) weatherConditions.temperature = tempMatch[1].replace(/^[-\s*]+/, '').trim();

    // Wind speed: 10.1 km/h
    const windMatch = sectionText.match(/Wind\s*(?:speed)?:\s*([^\n\r]+)/i);
    if (windMatch) weatherConditions.windSpeed = windMatch[1].replace(/^[-\s*]+/, '').trim();

    // Precipitation: 0.0 mm
    const precipMatch = sectionText.match(/Precipitation:\s*([^\n\r]+)/i);
    if (precipMatch) weatherConditions.precipitation = precipMatch[1].replace(/^[-\s*]+/, '').trim();

    // Precipitation probability: 19.0%
    const probMatch = sectionText.match(/Precipitation\s+probability:\s*([^\n\r]+)/i);
    if (probMatch) weatherConditions.precipitationProbability = probMatch[1].replace(/^[-\s*]+/, '').trim();

    // UV index: 8.85
    const uvMatch = sectionText.match(/UV\s+index:\s*([^\n\r]+)/i);
    if (uvMatch) weatherConditions.uvIndex = uvMatch[1].replace(/^[-\s*]+/, '').trim();

    // Collect all raw lines in case additional conditions are added
    const rawLines = sectionText
      .split('\n')
      .map(l => l.trim())
      .filter(l => l.startsWith('-') || l.startsWith('•'));
    if (rawLines.length > 0) {
      weatherConditions.rawItems = rawLines;
    }
  }

  // Extract Guidance
  const guidanceMatch = rawText.match(/Guidance:\s*([\s\S]*)$/i);
  const guidance = guidanceMatch ? guidanceMatch[1].trim() : undefined;

  return {
    isStructuredAdvisory: true,
    title: 'Weather Advisory',
    location,
    time,
    protocolId,
    severity,
    weatherConditions,
    guidance,
    rawText,
    fallbackType,
  };
}
