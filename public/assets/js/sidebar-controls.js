/**
 * Sidebar Controls - Filters and Layers
 * Handles filter interactions and layer toggles
 */

import { BASE_URL } from './api-service.js';

class SidebarControls {
  constructor() {
    this.filters = {
      basin: '',
      country: '',
      leadtime: '48',
      alert: '',
    };

    this.layers = {
      forecast: true,
      observations: false,
      'risk-zones': false,
      alerts: true,
    };

    this.stations = [];
    this.map = null;
    this.markers = null;
  }

  /**
   * Initialize sidebar controls
   */
  async init(map, markers) {
    this.map = map;
    this.markers = markers;

    // Initialize event listeners
    this.initFilterListeners();
    this.initLayerListeners();
    this.initResetButton();

    // Populate filter dropdowns
    await this.populateFilters();

    console.log('✅ Sidebar controls initialized');
  }

  /**
   * Initialize filter change listeners
   */
  initFilterListeners() {
    const basinFilter = document.getElementById('basin-filter');
    const countryFilter = document.getElementById('country-filter');
    const leadtimeFilter = document.getElementById('leadtime-filter');
    const alertFilter = document.getElementById('alert-filter');

    basinFilter?.addEventListener('change', (e) => {
      this.filters.basin = e.target.value;
      this.applyFilters();
    });

    countryFilter?.addEventListener('change', (e) => {
      this.filters.country = e.target.value;
      this.applyFilters();
    });

    leadtimeFilter?.addEventListener('change', (e) => {
      this.filters.leadtime = e.target.value;
      this.applyFilters();
    });

    alertFilter?.addEventListener('change', (e) => {
      this.filters.alert = e.target.value;
      this.applyFilters();
    });
  }

  /**
   * Initialize layer toggle listeners
   */
  initLayerListeners() {
    const layerInputs = document.querySelectorAll('.toggle-switch-input');

    layerInputs.forEach((input) => {
      input.addEventListener('change', (e) => {
        const layer = e.target.dataset.layer;
        this.layers[layer] = e.target.checked;
        this.toggleLayer(layer, e.target.checked);
      });
    });
  }

  /**
   * Initialize reset filters button
   */
  initResetButton() {
    const resetBtn = document.getElementById('reset-filters');

    resetBtn?.addEventListener('click', () => {
      this.resetFilters();
    });
  }

  /**
   * Populate filter dropdowns with data from API
   */
  async populateFilters() {
    try {
      const response = await fetch(`${BASE_URL}/v1/stations`);
      const stations = await response.json();
      this.stations = stations;

      // Extract unique basins and countries
      const basins = [...new Set(stations.map((s) => s.basin).filter(Boolean))].sort();
      const countries = [...new Set(stations.map((s) => s.country).filter(Boolean))].sort();

      // Populate basin dropdown
      const basinFilter = document.getElementById('basin-filter');
      if (basinFilter) {
        basins.forEach((basin) => {
          const option = document.createElement('option');
          option.value = basin;
          option.textContent = basin;
          basinFilter.appendChild(option);
        });
      }

      // Populate country dropdown
      const countryFilter = document.getElementById('country-filter');
      if (countryFilter) {
        countries.forEach((country) => {
          const option = document.createElement('option');
          option.value = country;
          option.textContent = country;
          countryFilter.appendChild(option);
        });
      }

      console.log(
        `📊 Loaded ${stations.length} stations, ${basins.length} basins, ${countries.length} countries`
      );
    } catch (error) {
      console.error('❌ Error populating filters:', error);
    }
  }

  /**
   * Apply current filters to map markers
   */
  applyFilters() {
    if (!this.markers) return;

    let visibleCount = 0;

    this.markers.eachLayer((marker) => {
      const station = marker.station;
      if (!station) return;

      let visible = true;

      // Apply basin filter
      if (this.filters.basin && station.basin !== this.filters.basin) {
        visible = false;
      }

      // Apply country filter
      if (this.filters.country && station.country !== this.filters.country) {
        visible = false;
      }

      // Apply alert filter (if station has alerts)
      if (this.filters.alert && station.alert_level !== this.filters.alert) {
        visible = false;
      }

      // Update marker visibility
      if (visible) {
        marker.addTo(this.map);
        visibleCount++;
      } else {
        marker.remove();
      }
    });

    console.log(`🔍 Filters applied: ${visibleCount} stations visible`);
    this.updateActiveFiltersDisplay();
  }

  /**
   * Toggle map layer visibility
   */
  toggleLayer(layerName, visible) {
    console.log(`🗺️ Layer "${layerName}" ${visible ? 'enabled' : 'disabled'}`);

    switch (layerName) {
      case 'forecast':
        // Toggle forecast markers
        if (this.markers) {
          if (visible) {
            this.markers.addTo(this.map);
          } else {
            this.markers.remove();
          }
        }
        break;

      case 'observations':
        // TODO: Implement observations layer
        console.log('📊 Observations layer - Coming soon!');
        break;

      case 'risk-zones':
        // TODO: Implement risk zones layer
        console.log('⚠️ Risk zones layer - Coming soon!');
        break;

      case 'alerts':
        // Toggle alert markers (could be styled differently)
        console.log('🚨 Alerts layer toggled');
        break;

      default:
        console.warn(`Unknown layer: ${layerName}`);
    }
  }

  /**
   * Reset all filters to default
   */
  resetFilters() {
    // Reset filter values
    this.filters = {
      basin: '',
      country: '',
      leadtime: '48',
      alert: '',
    };

    // Reset UI
    document.getElementById('basin-filter').value = '';
    document.getElementById('country-filter').value = '';
    document.getElementById('leadtime-filter').value = '48';
    document.getElementById('alert-filter').value = '';

    // Reapply filters (shows all)
    this.applyFilters();

    console.log('🔄 Filters reset');
  }

  /**
   * Update active filters display
   */
  updateActiveFiltersDisplay() {
    const container = document.getElementById('active-filters');
    const list = document.getElementById('active-filters-list');

    if (!container || !list) return;

    // Clear current list
    list.innerHTML = '';

    // Check if any filters are active
    const activeFilters = [];

    if (this.filters.basin) {
      activeFilters.push({ key: 'Basin', value: this.filters.basin, id: 'basin' });
    }
    if (this.filters.country) {
      activeFilters.push({ key: 'Country', value: this.filters.country, id: 'country' });
    }
    if (this.filters.leadtime && this.filters.leadtime !== '48') {
      activeFilters.push({ key: 'Lead Time', value: `${this.filters.leadtime}h`, id: 'leadtime' });
    }
    if (this.filters.alert) {
      const alertLabels = {
        extreme: '🔴 Extreme',
        severe: '🟠 Severe',
        warning: '🟡 Warning',
        info: '🔵 Info',
      };
      activeFilters.push({
        key: 'Alert',
        value: alertLabels[this.filters.alert] || this.filters.alert,
        id: 'alert',
      });
    }

    // Show/hide container
    if (activeFilters.length > 0) {
      container.style.display = 'block';

      // Add filter tags
      activeFilters.forEach((filter) => {
        const tag = document.createElement('div');
        tag.className = 'active-filter-tag';
        tag.innerHTML = `
          <span><strong>${filter.key}:</strong> ${filter.value}</span>
          <button class="active-filter-remove" data-filter="${filter.id}" title="Remove filter">×</button>
        `;

        // Add remove listener
        tag.querySelector('.active-filter-remove').addEventListener('click', () => {
          this.removeFilter(filter.id);
        });

        list.appendChild(tag);
      });
    } else {
      container.style.display = 'none';
    }
  }

  /**
   * Remove a specific filter
   */
  removeFilter(filterId) {
    this.filters[filterId] = filterId === 'leadtime' ? '48' : '';
    document.getElementById(`${filterId}-filter`).value = this.filters[filterId];
    this.applyFilters();
  }

  /**
   * Get current filter state
   */
  getFilters() {
    return { ...this.filters };
  }

  /**
   * Get current layer state
   */
  getLayers() {
    return { ...this.layers };
  }

  /**
   * Get filtered stations
   */
  getFilteredStations() {
    if (!this.stations || this.stations.length === 0) return [];

    return this.stations.filter((station) => {
      let matches = true;

      if (this.filters.basin && station.basin !== this.filters.basin) {
        matches = false;
      }

      if (this.filters.country && station.country !== this.filters.country) {
        matches = false;
      }

      if (this.filters.alert && station.alert_level !== this.filters.alert) {
        matches = false;
      }

      return matches;
    });
  }
}

// Export singleton instance
export const sidebarControls = new SidebarControls();
