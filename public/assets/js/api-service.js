/**
 * FloodSight API Service
 *
 * Handles all API communication with the FloodSight backend
 */

// API Configuration
const API_CONFIG = {
  // Use environment variable if available, otherwise detect based on hostname
  BASE_URL: (() => {
    // Priority 1: Use build-time environment variable if set
    // @ts-ignore - VITE_API_BASE_URL is injected at build time
    if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) {
      // @ts-ignore
      return import.meta.env.VITE_API_BASE_URL;
    }

    // Priority 2: Fallback to hostname-based detection for local development
    const hostname = window.location.hostname;

    // If accessing via local network IP (192.168.x.x), use backend API on port 30636
    if (
      hostname.startsWith('192.168.') ||
      hostname.startsWith('10.') ||
      hostname.startsWith('172.')
    ) {
      return 'http://192.168.178.50:30636/v1';
    }

    // If accessing via localhost, use Raspberry Pi backend API
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://192.168.178.50:30636/v1';
    }

    // Priority 3: Default production API (should not reach here if env var is set)
    return 'https://api.floodsight.com/v1';
  })(),

  TIMEOUT: 10000, // 10 seconds
};

// Export BASE_URL for use in other modules
export const BASE_URL = API_CONFIG.BASE_URL;

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  // Check if API is configured
  if (!API_CONFIG.BASE_URL) {
    throw new Error('API endpoint not configured - running in demo mode');
  }

  const url = `${API_CONFIG.BASE_URL}${endpoint}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error('Request timeout - API is not responding');
    }

    console.error(`API Error for ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Health Check
 * GET /health
 */
export async function getHealth() {
  return fetchAPI('/health');
}

/**
 * Transform station data from backend to frontend format
 */
function transformStation(station) {
  // Derive country from city name
  const cityCountryMap = {
    // Europe
    Berlin: 'Germany',
    Dresden: 'Germany',
    Cologne: 'Germany',
    Frankfurt: 'Germany',
    Vienna: 'Austria',
    Ferrara: 'Italy',
    Lyon: 'France',
    Warsaw: 'Poland',
    Kiev: 'Ukraine',
    Nizhny: 'Russia',
    // Asia
    Patna: 'India',
    Guwahati: 'India',
    Phnom: 'Cambodia',
    Wuhan: 'China',
    Hyderabad: 'Pakistan',
    Mandalay: 'Myanmar',
    Moulmein: 'Myanmar',
    // Africa
    Niamey: 'Niger',
    Khartoum: 'Sudan',
    Kinshasa: 'DR Congo',
    Tete: 'Mozambique',
    // Americas
    Manaus: 'Brazil',
    Corrientes: 'Argentina',
    Ciudad: 'Venezuela',
    Memphis: 'USA',
    Kansas: 'USA',
    // Australia
    Echuca: 'Australia',
  };

  // Extract city name from station name (e.g., "Berlin Spree" → "Berlin")
  const cityName = station.name.split(' ')[0];
  const country = cityCountryMap[cityName] || 'Unknown';

  return {
    ...station,
    station_code: station.code, // Map code → station_code
    river_name: station.river_basin, // Map river_basin → river_name
    country: country, // Add derived country
    // Ensure lat/lon are available as both formats
    latitude: station.lat ?? station.latitude,
    longitude: station.lon ?? station.longitude,
    lat: station.lat ?? station.latitude,
    lon: station.lon ?? station.longitude,
  };
}

/**
 * Get all stations
 * GET /stations
 */
export async function getStations(params = {}) {
  const queryParams = new URLSearchParams(params);
  const endpoint = `/stations${queryParams.toString() ? '?' + queryParams : ''}`;
  const stations = await fetchAPI(endpoint);

  // Transform stations to include frontend-expected fields
  return Array.isArray(stations) ? stations.map(transformStation) : stations;
}

/**
 * Get station by ID
 * GET /stations/{id}
 */
export async function getStationById(stationId) {
  return fetchAPI(`/stations/${stationId}`);
}

/**
 * Get forecasts
 * GET /forecasts
 */
export async function getForecasts(params = {}) {
  const queryParams = new URLSearchParams(params);
  const endpoint = `/forecasts${queryParams.toString() ? '?' + queryParams : ''}`;
  return fetchAPI(endpoint);
}

/**
 * Get forecasts for a specific station
 * GET /stations/{id}/forecasts
 */
export async function getStationForecasts(stationId, params = {}) {
  const queryParams = new URLSearchParams(params);
  const endpoint = `/stations/${stationId}/forecasts${queryParams.toString() ? '?' + queryParams : ''}`;
  return fetchAPI(endpoint);
}

/**
 * Get alerts
 * GET /alerts
 */
export async function getAlerts(params = {}) {
  const queryParams = new URLSearchParams(params);
  const endpoint = `/alerts${queryParams.toString() ? '?' + queryParams : ''}`;
  return fetchAPI(endpoint);
}

/**
 * Get alert by ID
 * GET /alerts/{id}
 */
export async function getAlertById(alertId) {
  return fetchAPI(`/alerts/${alertId}`);
}

/**
 * Get active alerts only
 * Convenience method for GET /alerts?active_only=true
 */
export async function getActiveAlerts() {
  return getAlerts({ active_only: 'true' });
}

/**
 * Ingest fake forecasts (development only)
 * POST /forecasts/ingest-dev
 */
export async function ingestFakeForecasts() {
  return fetchAPI('/forecasts/ingest-dev', { method: 'POST' });
}

/**
 * Compute alerts from forecasts
 * POST /alerts/compute
 */
export async function computeAlerts() {
  return fetchAPI('/alerts/compute', { method: 'POST' });
}

/**
 * Get Prometheus metrics
 * GET /metrics
 */
export async function getMetrics() {
  const url = `${API_CONFIG.BASE_URL}/metrics`;
  const response = await fetch(url);
  return await response.text(); // Metrics are text format
}

/**
 * Utility: Check if API is available
 */
export async function checkAPIConnection() {
  try {
    await getHealth();
    return { available: true, message: 'API is online' };
  } catch (error) {
    return {
      available: false,
      message: error.message || 'API is offline',
      error: error,
    };
  }
}

/**
 * Export API configuration for debugging
 */
export function getAPIConfig() {
  return {
    baseUrl: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
  };
}
