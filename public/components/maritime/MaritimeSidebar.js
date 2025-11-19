/**
 * MaritimeSidebar Component
 * Displays summary stats, alerts, ports table, and upgrade button
 */

export function createMaritimeSidebar() {
  return `
    <aside class="maritime-sidebar" role="complementary" aria-label="Maritime data summary">
      <!-- Header -->
      <div class="maritime-sidebar__header">
        <h1 class="maritime-sidebar__title">Maritime Edition</h1>
        <p class="maritime-sidebar__subtitle">
          Live vessel tracking, port monitoring & grounding risk
        </p>
      </div>

      <!-- Summary Cards -->
      <div id="summary-cards" class="summary-cards">
        <div class="summary-card">
          <p class="summary-card__value" id="stat-vessels">--</p>
          <p class="summary-card__label">Dark Vessels (24h)</p>
        </div>
        <div class="summary-card">
          <p class="summary-card__value" id="stat-plumes">--</p>
          <p class="summary-card__label">Active Plumes</p>
        </div>
        <div class="summary-card">
          <p class="summary-card__value" id="stat-ports">--</p>
          <p class="summary-card__label">High-Risk Ports</p>
        </div>
        <div class="summary-card">
          <p class="summary-card__value" id="stat-alerts">--</p>
          <p class="summary-card__label">Active Alerts</p>
        </div>
      </div>

      <!-- Recent Alerts -->
      <section class="maritime-section">
        <h2 class="maritime-section__title">Recent Alerts</h2>
        <div id="alerts-list" class="alerts-list">
          <!-- Will be populated dynamically -->
          <div class="empty-state">
            <p class="empty-state__message">Loading alerts...</p>
          </div>
        </div>
      </section>

      <!-- Top Ports -->
      <section class="maritime-section">
        <h2 class="maritime-section__title">Top Monitored Ports</h2>
        <div id="ports-table" class="ports-table">
          <!-- Will be populated dynamically -->
        </div>
      </section>

      <!-- Upgrade Button -->
      <button id="upgrade-button" class="upgrade-button" style="display: none;">
        <p class="upgrade-button__title">🚢 Upgrade to Maritime Edition</p>
        <p class="upgrade-button__subtitle">Unlock full vessel tracking & port monitoring</p>
      </button>
    </aside>
  `;
}

export function initMaritimeSidebar(demoData, userHasMaritimeAccess = true) {
  console.log('📊 Initializing Maritime Sidebar with data:', demoData);

  // Update summary cards
  updateSummaryCards(demoData.summary);

  // Populate alerts list
  populateAlertsList(demoData.alerts);

  // Populate ports table
  populatePortsTable(demoData.ports);

  // Show/hide upgrade button
  const upgradeButton = document.getElementById('upgrade-button');
  if (!userHasMaritimeAccess && upgradeButton) {
    upgradeButton.style.display = 'block';
    upgradeButton.addEventListener('click', handleUpgradeClick);
  }

  console.log('✅ Maritime sidebar initialized');
}

function updateSummaryCards(summary) {
  if (!summary) {
    console.warn('No summary data provided');
    return;
  }

  const statVessels = document.getElementById('stat-vessels');
  const statPlumes = document.getElementById('stat-plumes');
  const statPorts = document.getElementById('stat-ports');
  const statAlerts = document.getElementById('stat-alerts');

  if (statVessels) statVessels.textContent = summary.active_vessels_24h || 0;
  if (statPlumes) statPlumes.textContent = summary.active_plumes || 0;
  if (statPorts) statPorts.textContent = summary.high_risk_ports || 0;
  if (statAlerts) statAlerts.textContent = summary.recent_alerts || 0;

  console.log('✅ Summary cards updated');
}

function populateAlertsList(alerts) {
  const alertsList = document.getElementById('alerts-list');
  if (!alertsList) return;

  if (!alerts || alerts.length === 0) {
    alertsList.innerHTML = `
      <div class="empty-state">
        <p class="empty-state__title">All Clear</p>
        <p class="empty-state__message">No active maritime alerts</p>
      </div>
    `;
    return;
  }

  // Take only first 5 alerts
  const recentAlerts = alerts.slice(0, 5);

  alertsList.innerHTML = recentAlerts
    .map(
      (alert) => `
      <div class="alert-item alert-item--${alert.level}">
        <div class="alert-item__level">${alert.level}</div>
        <p class="alert-item__message">${escapeHtml(alert.message)}</p>
        <div class="alert-item__time">${formatRelativeTime(alert.created_at)}</div>
      </div>
    `
    )
    .join('');

  console.log(`✅ Populated ${recentAlerts.length} alerts`);
}

function populatePortsTable(ports) {
  const portsTableContainer = document.getElementById('ports-table');
  if (!portsTableContainer) return;

  if (!ports || ports.length === 0) {
    portsTableContainer.innerHTML = `
      <div class="empty-state">
        <p class="empty-state__message">No port data available</p>
      </div>
    `;
    return;
  }

  // Take only top 5 ports, sorted by safe draught (lowest first = highest risk)
  const topPorts = [...ports]
    .filter((p) => p.safe_draught_m !== null)
    .sort((a, b) => a.safe_draught_m - b.safe_draught_m)
    .slice(0, 5);

  if (topPorts.length === 0) {
    portsTableContainer.innerHTML = `
      <div class="empty-state">
        <p class="empty-state__message">No port draught data available</p>
      </div>
    `;
    return;
  }

  portsTableContainer.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Port</th>
          <th>Safe Draught</th>
          <th>24h Δ</th>
        </tr>
      </thead>
      <tbody>
        ${topPorts
          .map(
            (port) => `
          <tr>
            <td class="ports-table__port-name">${escapeHtml(port.name)}</td>
            <td class="ports-table__draught ${getDraughtClass(port.safe_draught_m)}">
              ${port.safe_draught_m.toFixed(2)} m
            </td>
            <td class="ports-table__change ${getChangeClass(port.change_24h)}">
              ${formatChange(port.change_24h)}
            </td>
          </tr>
        `
          )
          .join('')}
      </tbody>
    </table>
  `;

  console.log(`✅ Populated ${topPorts.length} ports`);
}

function getDraughtClass(draught) {
  if (draught >= 8) return 'ports-table__draught--safe';
  if (draught >= 5) return 'ports-table__draught--warning';
  return 'ports-table__draught--danger';
}

function getChangeClass(change) {
  if (!change) return '';
  return change >= 0 ? 'ports-table__change--positive' : 'ports-table__change--negative';
}

function formatChange(change) {
  if (change === null || change === undefined) return 'N/A';
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)} m`;
}

function formatRelativeTime(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function handleUpgradeClick() {
  alert(
    '🚢 Maritime Edition Upgrade\n\n' +
      'Contact sales to upgrade your FloodSight subscription:\n\n' +
      '• Full vessel detection & dark vessel monitoring\n' +
      '• Port safe draught & siltation risk\n' +
      '• Flood plume tracking with vessel analysis\n' +
      '• Grounding risk heatmaps\n\n' +
      'Email: maritime@floodsight.eu\n' +
      'Phone: +49 30 1234 5678'
  );
}

export function updateSidebarData(newData) {
  if (newData.summary) {
    updateSummaryCards(newData.summary);
  }

  if (newData.alerts) {
    populateAlertsList(newData.alerts);
  }

  if (newData.ports) {
    populatePortsTable(newData.ports);
  }

  console.log('✅ Sidebar data updated');
}

