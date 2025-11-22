/**
 * Frontend Error Reporting and Telemetry Client
 *
 * Captures client-side errors and sends them to the backend for logging.
 * Supports both global error handlers and manual error reporting.
 */

import { BASE_URL } from './api-service.js';

/**
 * Error reporter configuration
 */
const config = {
  apiUrl: BASE_URL,
  enabled: true, // Can be controlled via environment variable
  maxRetries: 2,
  retryDelay: 1000, // ms
};

/**
 * Send telemetry event to backend
 * @param {string} eventName - Name of the event
 * @param {object} context - Additional context data
 * @returns {Promise<void>}
 */
async function sendTelemetry(eventName, context = {}) {
  if (!config.enabled) {
    console.log('[Telemetry] Disabled, skipping:', eventName);
    return;
  }

  const event = {
    event_name: eventName,
    timestamp: new Date().toISOString(),
    page: window.location.pathname,
    user_agent: navigator.userAgent,
    context: {
      ...context,
      screen_width: window.screen.width,
      screen_height: window.screen.height,
      viewport_width: window.innerWidth,
      viewport_height: window.innerHeight,
    },
  };

  try {
    const response = await fetch(`${config.apiUrl}/telemetry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(event),
    });

    if (!response.ok) {
      console.error('[Telemetry] Failed to send event:', response.statusText);
    }
  } catch (error) {
    console.error('[Telemetry] Network error:', error);
  }
}

/**
 * Report an error to the backend
 * @param {Error|string} error - The error to report
 * @param {object} context - Additional context data
 * @returns {Promise<void>}
 */
export async function reportError(error, context = {}) {
  const errorData = {
    message: error.message || String(error),
    stack: error.stack || new Error().stack,
    type: error.name || 'Error',
    ...context,
  };

  console.error('[ErrorReporter] Capturing error:', errorData);

  await sendTelemetry('client_error', errorData);
}

/**
 * Report a custom event
 * @param {string} eventName - Name of the event
 * @param {object} data - Event data
 * @returns {Promise<void>}
 */
export async function reportEvent(eventName, data = {}) {
  console.log('[Telemetry] Tracking event:', eventName, data);
  await sendTelemetry(eventName, data);
}

/**
 * Initialize error tracking
 * Sets up global error handlers
 */
export function initErrorTracking() {
  console.log('[ErrorReporter] Initializing error tracking...');

  // Global error handler
  window.addEventListener('error', (event) => {
    reportError(event.error || new Error(event.message), {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      source: 'window.onerror',
    });
  });

  // Unhandled promise rejection handler
  window.addEventListener('unhandledrejection', (event) => {
    reportError(event.reason || new Error('Unhandled Promise Rejection'), {
      promise: String(event.promise),
      source: 'unhandledrejection',
    });
  });

  // Track page load performance
  window.addEventListener('load', () => {
    // Use setTimeout to ensure performance metrics are available
    setTimeout(() => {
      const perfData = window.performance.timing;
      const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
      const domReadyTime = perfData.domContentLoadedEventEnd - perfData.navigationStart;

      reportEvent('page_load', {
        page_load_time: pageLoadTime,
        dom_ready_time: domReadyTime,
        page: window.location.pathname,
      });
    }, 0);
  });

  console.log('[ErrorReporter] Error tracking initialized successfully');
}

/**
 * Track important user interactions
 * Call this for significant user actions
 * @param {string} action - Action name
 * @param {object} data - Action data
 */
export function trackAction(action, data = {}) {
  reportEvent(`user_action.${action}`, data);
}

// Auto-initialize on module load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initErrorTracking);
} else {
  // DOM is already loaded
  initErrorTracking();
}

// Export configuration for testing
export { config };
