/**
 * SidebarFilters Component
 * Sidebar with filters for Basin, Country, Lead Time, and toggle groups
 */

export function createSidebarFilters() {
  return `
    <aside class="sidebar-filters" role="complementary" aria-label="Filters">
      <div class="sidebar-filters__header">
        <h2 class="sidebar-filters__title">Filters</h2>
      </div>
      
      <div class="sidebar-filters__content">
        <!-- Basin Filter -->
        <div class="filter-group">
          <label class="filter-group__label" for="basin-select">Basin</label>
          <select id="basin-select" class="filter-group__select">
            <option value="">All Basins</option>
            <option value="rhine">Rhine</option>
            <option value="danube">Danube</option>
            <option value="elbe">Elbe</option>
            <option value="po">Po</option>
            <option value="loire">Loire</option>
          </select>
        </div>

        <!-- Country Filter -->
        <div class="filter-group">
          <label class="filter-group__label" for="country-select">Country</label>
          <select id="country-select" class="filter-group__select">
            <option value="">All Countries</option>
            <option value="de">Germany</option>
            <option value="fr">France</option>
            <option value="it">Italy</option>
            <option value="nl">Netherlands</option>
            <option value="at">Austria</option>
          </select>
        </div>

        <!-- Lead Time Filter -->
        <div class="filter-group">
          <label class="filter-group__label" for="leadtime-select">Lead Time</label>
          <select id="leadtime-select" class="filter-group__select">
            <option value="24">24 hours</option>
            <option value="48" selected>48 hours</option>
            <option value="72">72 hours</option>
            <option value="120">5 days</option>
            <option value="168">7 days</option>
          </select>
        </div>

        <!-- Toggle Groups -->
        <div class="filter-group">
          <span class="filter-group__label">Data Layers</span>
          <div class="toggle-group">
            <label class="toggle-item">
              <input type="checkbox" checked />
              <span>Forecast</span>
            </label>
            <label class="toggle-item">
              <input type="checkbox" checked />
              <span>Observations</span>
            </label>
            <label class="toggle-item">
              <input type="checkbox" />
              <span>Risk Zones</span>
            </label>
          </div>
        </div>

        <!-- Apply Button -->
        <button class="btn btn--primary" style="width: 100%; margin-top: 16px;">
          Apply Filters
        </button>
      </div>
    </aside>
  `;
}

export function initSidebarFilters() {
  console.log('SidebarFilters initialized');
  // Add filter change handlers here
}
