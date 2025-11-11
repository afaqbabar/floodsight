/**
 * MapPanel Component
 * Main map container for displaying flood data
 */

export function createMapPanel() {
  return `
    <div class="map-panel" role="main" aria-label="Flood map">
      <div class="map-panel__container">
        <div class="map-panel__placeholder">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          <h3>Map View</h3>
          <p class="map-panel__placeholder-text">
            Interactive map will be displayed here.<br />
            Showing European river basins and flood forecasts.
          </p>
          <div class="map-panel__stats">
            <div class="stat-item">
              <span class="stat-item__value">127</span>
              <span class="stat-item__label">Stations</span>
            </div>
            <div class="stat-item">
              <span class="stat-item__value">5</span>
              <span class="stat-item__label">Active Alerts</span>
            </div>
            <div class="stat-item">
              <span class="stat-item__value">48h</span>
              <span class="stat-item__label">Forecast</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export function initMapPanel() {
  console.log('MapPanel initialized');
  // Initialize map library here (e.g., Leaflet, Mapbox)
}
