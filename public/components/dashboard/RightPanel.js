/**
 * RightPanel Component
 * Right sidebar with forecast cards and CTAs
 */

export function createRightPanel() {
  return `
    <aside class="right-panel" role="complementary" aria-label="Forecast details">
      <div class="right-panel__header">
        <h2 class="right-panel__title">Forecast Details</h2>
      </div>
      
      <div class="right-panel__content">
        <!-- Forecast Cards -->
        <div class="forecast-card">
          <div class="forecast-card__header">
            <h3 class="forecast-card__title">Rhine Basin</h3>
            <span class="forecast-card__status forecast-card__status--warning">Warning</span>
          </div>
          <div class="forecast-card__body">
            <div class="forecast-metric">
              <span class="forecast-metric__label">Water Level</span>
              <span class="forecast-metric__value">4.2m</span>
            </div>
            <div class="forecast-metric">
              <span class="forecast-metric__label">Peak Expected</span>
              <span class="forecast-metric__value">In 36h</span>
            </div>
            <div class="forecast-metric">
              <span class="forecast-metric__label">Risk Level</span>
              <span class="forecast-metric__value">Medium</span>
            </div>
          </div>
          <button class="btn btn--ghost" style="width: 100%; margin-top: 8px;">
            View Details
          </button>
        </div>

        <div class="forecast-card">
          <div class="forecast-card__header">
            <h3 class="forecast-card__title">Danube Basin</h3>
            <span class="forecast-card__status forecast-card__status--normal">Normal</span>
          </div>
          <div class="forecast-card__body">
            <div class="forecast-metric">
              <span class="forecast-metric__label">Water Level</span>
              <span class="forecast-metric__value">2.8m</span>
            </div>
            <div class="forecast-metric">
              <span class="forecast-metric__label">Trend</span>
              <span class="forecast-metric__value">Stable</span>
            </div>
            <div class="forecast-metric">
              <span class="forecast-metric__label">Risk Level</span>
              <span class="forecast-metric__value">Low</span>
            </div>
          </div>
          <button class="btn btn--ghost" style="width: 100%; margin-top: 8px;">
            View Details
          </button>
        </div>

        <!-- CTA Section -->
        <div class="right-panel__cta">
          <h3 style="margin: 0 0 8px; font-size: 14px;">Need Real-Time Alerts?</h3>
          <p style="margin: 0 0 12px; font-size: 13px; color: var(--muted);">
            Get notified when flood risks are detected in your areas of interest.
          </p>
          <button class="btn btn--primary" style="width: 100%;">
            Create Alert
          </button>
        </div>
      </div>
    </aside>
  `;
}

export function initRightPanel() {
  console.log('RightPanel initialized');
  // Add click handlers for forecast cards
}

