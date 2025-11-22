/**
 * MaritimeMap Component
 * Full-screen MapLibre GL JS map with 4 maritime layers
 */

let map = null;
let layersData = {
  vessels: null,
  plumes: null,
  groundingRisk: null,
  ports: null,
};

export function createMaritimeMap() {
  return `
    <div class="maritime-map" role="main" aria-label="Maritime monitoring map">
      <div id="map-container" class="maritime-map__container"></div>
      
      <!-- Layer Toggles -->
      <div class="layer-toggles">
        <h3 class="layer-toggles__title">Map Layers</h3>
        <div class="layer-toggles__list">
          <label class="layer-toggle">
            <input 
              type="checkbox" 
              class="layer-toggle__checkbox" 
              id="toggle-vessels" 
              checked
            />
            <div class="layer-toggle__icon layer-toggle__icon--vessels"></div>
            <span class="layer-toggle__label">Dark Vessels</span>
          </label>
          
          <label class="layer-toggle">
            <input 
              type="checkbox" 
              class="layer-toggle__checkbox" 
              id="toggle-plumes" 
              checked
            />
            <div class="layer-toggle__icon layer-toggle__icon--plumes"></div>
            <span class="layer-toggle__label">Flood Plumes</span>
          </label>
          
          <label class="layer-toggle">
            <input 
              type="checkbox" 
              class="layer-toggle__checkbox" 
              id="toggle-grounding" 
              checked
            />
            <div class="layer-toggle__icon layer-toggle__icon--grounding"></div>
            <span class="layer-toggle__label">Grounding Risk</span>
          </label>
          
          <label class="layer-toggle">
            <input 
              type="checkbox" 
              class="layer-toggle__checkbox" 
              id="toggle-ports" 
              checked
            />
            <div class="layer-toggle__icon layer-toggle__icon--ports"></div>
            <span class="layer-toggle__label">Port Fairways</span>
          </label>
        </div>
      </div>
      
      <!-- Loading State -->
      <div id="map-loading" class="maritime-loading" style="display: none;">
        <div class="maritime-loading__spinner"></div>
        <p>Loading maritime data...</p>
      </div>
    </div>
  `;
}

export async function initMaritimeMap(demoData) {
  console.log('🗺️ Initializing Maritime Map with data:', demoData);

  // Check if MapLibre GL is loaded
  if (typeof maplibregl === 'undefined') {
    console.error('❌ MapLibre GL JS is not loaded. Add it to the HTML.');
    return;
  }

  // Store data
  layersData = {
    vessels: demoData.vessels,
    plumes: demoData.plumes,
    groundingRisk: demoData.grounding_risk,
    ports: demoData.ports,
  };

  // Initialize map centered on Europe
  map = new maplibregl.Map({
    container: 'map-container',
    style: {
      version: 8,
      sources: {
        'osm-tiles': {
          type: 'raster',
          tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
          tileSize: 256,
          attribution: '© OpenStreetMap contributors',
        },
      },
      layers: [
        {
          id: 'osm-background',
          type: 'raster',
          source: 'osm-tiles',
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    },
    center: [10.0, 51.0], // Center of Germany
    zoom: 5,
    attributionControl: true,
  });

  // Wait for map to load
  map.on('load', () => {
    console.log('✅ Map loaded, adding maritime layers...');

    // Add all layers
    addVesselsLayer();
    addPlumesLayer();
    addGroundingRiskLayer();
    addPortsLayer();

    // Setup layer toggles
    setupLayerToggles();

    console.log('✅ Maritime map initialized with all layers');
  });

  // Add navigation controls
  map.addControl(new maplibregl.NavigationControl(), 'bottom-right');
}

function addVesselsLayer() {
  if (!layersData.vessels || layersData.vessels.features.length === 0) {
    console.log('No vessel data to display');
    return;
  }

  map.addSource('vessels', {
    type: 'geojson',
    data: layersData.vessels,
  });

  // Add vessel circles
  map.addLayer({
    id: 'vessels-circles',
    type: 'circle',
    source: 'vessels',
    paint: {
      'circle-radius': 6,
      'circle-color': '#ef4444',
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
      'circle-opacity': 0.8,
    },
  });

  // Add popup on click
  map.on('click', 'vessels-circles', (e) => {
    const props = e.features[0].properties;
    const coordinates = e.features[0].geometry.coordinates.slice();

    new maplibregl.Popup()
      .setLngLat(coordinates)
      .setHTML(
        `
        <div style="padding: 8px;">
          <strong>Dark Vessel Detected</strong><br/>
          <small>Confidence: ${(props.confidence * 100).toFixed(1)}%</small><br/>
          <small>Length: ${props.vessel_length_m?.toFixed(1) || 'N/A'} m</small><br/>
          <small>Time: ${new Date(props.detection_time).toLocaleString()}</small>
        </div>
      `
      )
      .addTo(map);
  });

  // Change cursor on hover
  map.on('mouseenter', 'vessels-circles', () => {
    map.getCanvas().style.cursor = 'pointer';
  });
  map.on('mouseleave', 'vessels-circles', () => {
    map.getCanvas().style.cursor = '';
  });

  console.log(`✅ Added ${layersData.vessels.features.length} vessels to map`);
}

function addPlumesLayer() {
  if (!layersData.plumes || layersData.plumes.features.length === 0) {
    console.log('No plume data to display');
    return;
  }

  map.addSource('plumes', {
    type: 'geojson',
    data: layersData.plumes,
  });

  // Add plume polygons
  map.addLayer({
    id: 'plumes-fill',
    type: 'fill',
    source: 'plumes',
    paint: {
      'fill-color': '#f59e0b',
      'fill-opacity': 0.3,
    },
  });

  // Add plume borders
  map.addLayer({
    id: 'plumes-line',
    type: 'line',
    source: 'plumes',
    paint: {
      'line-color': '#f59e0b',
      'line-width': 2,
    },
  });

  // Add popup on click
  map.on('click', 'plumes-fill', (e) => {
    const props = e.features[0].properties;

    new maplibregl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(
        `
        <div style="padding: 8px;">
          <strong>Flood Plume</strong><br/>
          <small>River: ${props.river || 'Unknown'}</small><br/>
          <small>Peak Discharge: ${props.peak_discharge || 'N/A'} m³/s</small><br/>
          <small>Vessels Inside: ${props.vessel_count || 0}</small>
        </div>
      `
      )
      .addTo(map);
  });

  map.on('mouseenter', 'plumes-fill', () => {
    map.getCanvas().style.cursor = 'pointer';
  });
  map.on('mouseleave', 'plumes-fill', () => {
    map.getCanvas().style.cursor = '';
  });

  console.log(`✅ Added ${layersData.plumes.features.length} plumes to map`);
}

function addGroundingRiskLayer() {
  if (!layersData.groundingRisk || layersData.groundingRisk.features.length === 0) {
    console.log('No grounding risk data to display');
    return;
  }

  map.addSource('grounding-risk', {
    type: 'geojson',
    data: layersData.groundingRisk,
  });

  // Add grounding risk heatmap
  map.addLayer({
    id: 'grounding-risk-fill',
    type: 'fill',
    source: 'grounding-risk',
    paint: {
      'fill-color': [
        'match',
        ['get', 'risk'],
        'safe',
        '#10b981',
        'moderate',
        '#f59e0b',
        'high',
        '#ef4444',
        '#94a3b8', // default
      ],
      'fill-opacity': 0.4,
    },
  });

  // Add borders
  map.addLayer({
    id: 'grounding-risk-line',
    type: 'line',
    source: 'grounding-risk',
    paint: {
      'line-color': '#ffffff',
      'line-width': 1,
    },
  });

  console.log(
    `✅ Added grounding risk layer with ${layersData.groundingRisk.features.length} features`
  );
}

function addPortsLayer() {
  if (!layersData.ports || layersData.ports.length === 0) {
    console.log('No port data to display');
    return;
  }

  // Convert ports array to GeoJSON (assume they have geometry)
  const portsGeoJSON = {
    type: 'FeatureCollection',
    features: layersData.ports
      .filter((p) => p.geometry)
      .map((port) => ({
        type: 'Feature',
        geometry: port.geometry,
        properties: {
          name: port.name,
          safe_draught_m: port.safe_draught_m,
          change_24h: port.change_24h,
        },
      })),
  };

  if (portsGeoJSON.features.length === 0) {
    console.log('No port geometry available');
    return;
  }

  map.addSource('ports', {
    type: 'geojson',
    data: portsGeoJSON,
  });

  // Add port polygons
  map.addLayer({
    id: 'ports-fill',
    type: 'fill',
    source: 'ports',
    paint: {
      'fill-color': '#3b82f6',
      'fill-opacity': 0.2,
    },
  });

  // Add port borders
  map.addLayer({
    id: 'ports-line',
    type: 'line',
    source: 'ports',
    paint: {
      'line-color': '#3b82f6',
      'line-width': 2,
    },
  });

  // Add popup on click
  map.on('click', 'ports-fill', (e) => {
    const props = e.features[0].properties;

    new maplibregl.Popup()
      .setLngLat(e.lngLat)
      .setHTML(
        `
        <div style="padding: 8px;">
          <strong>${props.name}</strong><br/>
          <small>Safe Draught: ${props.safe_draught_m?.toFixed(2) || 'N/A'} m</small><br/>
          <small>24h Change: ${props.change_24h ? (props.change_24h > 0 ? '+' : '') + props.change_24h.toFixed(2) + ' m' : 'N/A'}</small>
        </div>
      `
      )
      .addTo(map);
  });

  map.on('mouseenter', 'ports-fill', () => {
    map.getCanvas().style.cursor = 'pointer';
  });
  map.on('mouseleave', 'ports-fill', () => {
    map.getCanvas().style.cursor = '';
  });

  console.log(`✅ Added ${portsGeoJSON.features.length} ports to map`);
}

function setupLayerToggles() {
  const toggles = {
    vessels: document.getElementById('toggle-vessels'),
    plumes: document.getElementById('toggle-plumes'),
    grounding: document.getElementById('toggle-grounding'),
    ports: document.getElementById('toggle-ports'),
  };

  // Vessels toggle
  toggles.vessels?.addEventListener('change', (e) => {
    const visibility = e.target.checked ? 'visible' : 'none';
    if (map.getLayer('vessels-circles')) {
      map.setLayoutProperty('vessels-circles', 'visibility', visibility);
    }
  });

  // Plumes toggle
  toggles.plumes?.addEventListener('change', (e) => {
    const visibility = e.target.checked ? 'visible' : 'none';
    if (map.getLayer('plumes-fill')) {
      map.setLayoutProperty('plumes-fill', 'visibility', visibility);
      map.setLayoutProperty('plumes-line', 'visibility', visibility);
    }
  });

  // Grounding risk toggle
  toggles.grounding?.addEventListener('change', (e) => {
    const visibility = e.target.checked ? 'visible' : 'none';
    if (map.getLayer('grounding-risk-fill')) {
      map.setLayoutProperty('grounding-risk-fill', 'visibility', visibility);
      map.setLayoutProperty('grounding-risk-line', 'visibility', visibility);
    }
  });

  // Ports toggle
  toggles.ports?.addEventListener('change', (e) => {
    const visibility = e.target.checked ? 'visible' : 'none';
    if (map.getLayer('ports-fill')) {
      map.setLayoutProperty('ports-fill', 'visibility', visibility);
      map.setLayoutProperty('ports-line', 'visibility', visibility);
    }
  });

  console.log('✅ Layer toggles configured');
}

export function updateMapData(newData) {
  if (!map) {
    console.error('Map not initialized');
    return;
  }

  // Update sources if they exist
  if (newData.vessels && map.getSource('vessels')) {
    map.getSource('vessels').setData(newData.vessels);
  }

  if (newData.plumes && map.getSource('plumes')) {
    map.getSource('plumes').setData(newData.plumes);
  }

  if (newData.grounding_risk && map.getSource('grounding-risk')) {
    map.getSource('grounding-risk').setData(newData.grounding_risk);
  }

  console.log('✅ Map data updated');
}
