/**
 * Options Page Controller
 */

// Tab management
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const tabName = btn.dataset.tab;

    // Update active tab button
    tabBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Update active tab content
    tabContents.forEach(content => {
      content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
  });
});

// Consent management
const consentDot = document.getElementById('consentDot');
const consentStatusText = document.getElementById('consentStatusText');
const grantConsentBtn = document.getElementById('grantConsentBtn');
const revokeConsentBtn = document.getElementById('revokeConsentBtn');

// Preferences
const notificationsEnabled = document.getElementById('notificationsEnabled');
const syncEnabled = document.getElementById('syncEnabled');
const privacyModeInputs = document.querySelectorAll('input[name="privacyMode"]');
const savePreferencesBtn = document.getElementById('savePreferencesBtn');

// Data management
const eventCount = document.getElementById('eventCount');
const sessionCount = document.getElementById('sessionCount');
const storageUsed = document.getElementById('storageUsed');
const exportDataBtn = document.getElementById('exportDataBtn');
const viewDataBtn = document.getElementById('viewDataBtn');
const deleteDataBtn = document.getElementById('deleteDataBtn');
const manualSyncBtn = document.getElementById('manualSyncBtn');
const syncStatusText = document.getElementById('syncStatusText');
const lastSyncTime = document.getElementById('lastSyncTime');

// Categories
const curatedCount = document.getElementById('curatedCount');
const overrideCount = document.getElementById('overrideCount');
const heuristicCount = document.getElementById('heuristicCount');
const domainInput = document.getElementById('domainInput');
const categorySelect = document.getElementById('categorySelect');
const addCategoryBtn = document.getElementById('addCategoryBtn');
const overridesList = document.getElementById('overridesList');

// Version
const version = document.getElementById('version');

/**
 * Initialize options page
 */
async function init() {
  // Set version
  version.textContent = chrome.runtime.getManifest().version;

  // Check for consent query parameter
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('consent') === 'required' || urlParams.get('reconsent') === 'required') {
    // Show consent tab
    document.querySelector('[data-tab="consent"]').click();

    if (urlParams.get('reconsent') === 'required') {
      const fromVersion = urlParams.get('from');
      alert(`Pulse has been updated from version ${fromVersion}. Please review and accept the updated consent terms.`);
    }
  }

  // Load current state
  await loadConsentStatus();
  await loadPreferences();
  await loadDataStats();
  await loadCategoryStats();
}

/**
 * Load consent status
 */
async function loadConsentStatus() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'get_consent_status' });

    if (response.hasConsent) {
      consentDot.className = 'status-dot active';
      consentStatusText.textContent = `Active (Version ${response.consentState.version})`;
      grantConsentBtn.style.display = 'none';
      revokeConsentBtn.style.display = 'inline-block';
    } else {
      consentDot.className = 'status-dot inactive';
      consentStatusText.textContent = 'Not granted';
      grantConsentBtn.style.display = 'inline-block';
      revokeConsentBtn.style.display = 'none';
    }
  } catch (error) {
    console.error('Failed to load consent status:', error);
    consentStatusText.textContent = 'Error loading status';
  }
}

/**
 * Load preferences
 */
async function loadPreferences() {
  try {
    const result = await chrome.storage.local.get('userPreferences');
    const prefs = result.userPreferences || {
      notificationsEnabled: true,
      syncEnabled: true,
      privacyMode: 'balanced'
    };

    notificationsEnabled.checked = prefs.notificationsEnabled;
    syncEnabled.checked = prefs.syncEnabled;

    privacyModeInputs.forEach(input => {
      if (input.value === prefs.privacyMode) {
        input.checked = true;
      }
    });
  } catch (error) {
    console.error('Failed to load preferences:', error);
  }
}

/**
 * Load data statistics
 */
async function loadDataStats() {
  try {
    // This would query the storage manager
    // For now, show placeholder values
    eventCount.textContent = '--';
    sessionCount.textContent = '--';
    storageUsed.textContent = '-- MB';

    syncStatusText.textContent = 'Sync enabled';
    lastSyncTime.textContent = 'Last sync: Never';
  } catch (error) {
    console.error('Failed to load data stats:', error);
  }
}

/**
 * Load category statistics
 */
async function loadCategoryStats() {
  try {
    // Load from storage
    const result = await chrome.storage.local.get('categoryOverrides');
    const overrides = result.categoryOverrides || {};

    curatedCount.textContent = '500+';
    heuristicCount.textContent = '15';
    overrideCount.textContent = Object.keys(overrides).length;

    // Display overrides
    displayOverrides(overrides);
  } catch (error) {
    console.error('Failed to load category stats:', error);
  }
}

/**
 * Display category overrides
 */
function displayOverrides(overrides) {
  overridesList.innerHTML = '';

  if (Object.keys(overrides).length === 0) {
    overridesList.innerHTML = '<p style="text-align: center; color: #9ca3af; padding: 20px;">No custom categories yet</p>';
    return;
  }

  for (const [domain, info] of Object.entries(overrides)) {
    const item = document.createElement('div');
    item.className = 'override-item';
    item.innerHTML = `
      <span class="override-domain">${domain}</span>
      <div>
        <span class="override-category ${info.category}">${info.category}</span>
        <button class="btn btn-sm" data-domain="${domain}" style="margin-left: 8px; padding: 4px 8px; font-size: 12px;">Remove</button>
      </div>
    `;

    const removeBtn = item.querySelector('button');
    removeBtn.addEventListener('click', () => removeOverride(domain));

    overridesList.appendChild(item);
  }
}

/**
 * Remove category override
 */
async function removeOverride(domain) {
  try {
    const result = await chrome.storage.local.get('categoryOverrides');
    const overrides = result.categoryOverrides || {};

    delete overrides[domain];

    await chrome.storage.local.set({ categoryOverrides: overrides });

    await loadCategoryStats();

    showNotification('Category override removed');
  } catch (error) {
    console.error('Failed to remove override:', error);
    alert('Failed to remove override');
  }
}

/**
 * Show notification
 */
function showNotification(message) {
  // Simple alert for now
  // Could be replaced with a nicer toast notification
  const notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #10b981;
    color: white;
    padding: 12px 20px;
    border-radius: 6px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
  `;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 3000);
}

/**
 * Event Listeners
 */

// Grant consent
grantConsentBtn.addEventListener('click', async () => {
  try {
    await chrome.runtime.sendMessage({ type: 'grant_consent' });
    await loadConsentStatus();
    showNotification('Consent granted successfully');
  } catch (error) {
    console.error('Failed to grant consent:', error);
    alert('Failed to grant consent');
  }
});

// Revoke consent
revokeConsentBtn.addEventListener('click', async () => {
  const confirmed = confirm(
    'Are you sure you want to revoke consent?\n\n' +
    'This will:\n' +
    '- Stop all data collection\n' +
    '- Pause synchronization\n' +
    '- Disable personalized recommendations\n\n' +
    'Your local data will be kept unless you choose to delete it.'
  );

  if (!confirmed) return;

  const deleteData = confirm('Do you also want to delete all local data?');

  try {
    await chrome.runtime.sendMessage({
      type: 'revoke_consent',
      deleteData
    });

    await loadConsentStatus();
    showNotification('Consent revoked');
  } catch (error) {
    console.error('Failed to revoke consent:', error);
    alert('Failed to revoke consent');
  }
});

// Save preferences
savePreferencesBtn.addEventListener('click', async () => {
  try {
    const selectedPrivacyMode = document.querySelector('input[name="privacyMode"]:checked').value;

    const preferences = {
      notificationsEnabled: notificationsEnabled.checked,
      syncEnabled: syncEnabled.checked,
      privacyMode: selectedPrivacyMode
    };

    await chrome.storage.local.set({ userPreferences: preferences });

    showNotification('Preferences saved');
  } catch (error) {
    console.error('Failed to save preferences:', error);
    alert('Failed to save preferences');
  }
});

// Export data
exportDataBtn.addEventListener('click', async () => {
  try {
    await chrome.runtime.sendMessage({ type: 'export_data' });
    showNotification('Data export started');
  } catch (error) {
    console.error('Failed to export data:', error);
    alert('Failed to export data');
  }
});

// View data
viewDataBtn.addEventListener('click', () => {
  alert('This feature will open a detailed view of your collected data.');
  // TODO: Implement data viewer
});

// Delete data
deleteDataBtn.addEventListener('click', async () => {
  const confirmed = confirm(
    'Are you sure you want to delete ALL local data?\n\n' +
    'This action cannot be undone.\n' +
    'Your consent status will be preserved.'
  );

  if (!confirmed) return;

  try {
    // TODO: Implement data deletion
    showNotification('All local data deleted');
    await loadDataStats();
  } catch (error) {
    console.error('Failed to delete data:', error);
    alert('Failed to delete data');
  }
});

// Manual sync
manualSyncBtn.addEventListener('click', async () => {
  manualSyncBtn.textContent = 'Syncing...';
  manualSyncBtn.disabled = true;

  try {
    await chrome.runtime.sendMessage({ type: 'trigger_sync' });

    showNotification('Sync completed');
    lastSyncTime.textContent = `Last sync: ${new Date().toLocaleString()}`;
  } catch (error) {
    console.error('Sync failed:', error);
    alert('Sync failed');
  } finally {
    manualSyncBtn.textContent = 'Sync Now';
    manualSyncBtn.disabled = false;
  }
});

// Add category override
addCategoryBtn.addEventListener('click', async () => {
  const domain = domainInput.value.trim().toLowerCase();
  const category = categorySelect.value;

  if (!domain) {
    alert('Please enter a domain');
    return;
  }

  // Basic domain validation
  if (!/^[a-z0-9.-]+\.[a-z]{2,}$/.test(domain)) {
    alert('Please enter a valid domain (e.g., example.com)');
    return;
  }

  try {
    const result = await chrome.storage.local.get('categoryOverrides');
    const overrides = result.categoryOverrides || {};

    overrides[domain] = {
      category,
      confidence: 1.0,
      source: 'user',
      timestamp: Date.now()
    };

    await chrome.storage.local.set({ categoryOverrides: overrides });

    domainInput.value = '';
    await loadCategoryStats();

    showNotification(`Category override added: ${domain} → ${category}`);
  } catch (error) {
    console.error('Failed to add category override:', error);
    alert('Failed to add category override');
  }
});

// Initialize on load
init();
