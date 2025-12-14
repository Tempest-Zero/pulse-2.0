/**
 * Service Worker (Background Script)
 * Handles extension lifecycle, data collection, and synchronization
 */

import storageManager from '../lib/storage-manager.js';
import consentManager from '../lib/consent-manager.js';
import syncScheduler from '../lib/sync-scheduler.js';
import aggregator from '../lib/aggregator.js';

// Extension state
let extensionInitialized = false;
let dataCollectionActive = false;

/**
 * Initialize extension on installation
 */
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('Extension installed:', details.reason);

  if (details.reason === 'install') {
    // First-time installation
    await handleFirstInstall();
  } else if (details.reason === 'update') {
    // Extension updated
    await handleUpdate(details.previousVersion);
  }

  await initializeExtension();
});

/**
 * Initialize extension on startup
 */
chrome.runtime.onStartup.addListener(async () => {
  console.log('Extension started');
  await initializeExtension();
});

/**
 * Handle first-time installation
 */
async function handleFirstInstall() {
  console.log('First-time installation - showing consent dialog');

  // Open options page for consent
  chrome.tabs.create({
    url: chrome.runtime.getURL('options/options.html?consent=required')
  });

  // Set default preferences
  await chrome.storage.local.set({
    userPreferences: {
      notificationsEnabled: true,
      syncEnabled: true,
      privacyMode: 'balanced' // strict, balanced, or minimal
    }
  });
}

/**
 * Handle extension update
 */
async function handleUpdate(previousVersion) {
  console.log(`Extension updated from ${previousVersion} to ${chrome.runtime.getManifest().version}`);

  // Check if consent re-validation is needed
  await consentManager.init();

  const currentVersion = chrome.runtime.getManifest().version;
  const upgradeResult = await consentManager.handleVersionUpgrade(currentVersion);

  if (upgradeResult.action === 'reconsent_required') {
    // Show re-consent dialog
    chrome.tabs.create({
      url: chrome.runtime.getURL(`options/options.html?reconsent=required&from=${previousVersion}`)
    });
  } else if (upgradeResult.action === 'auto_upgraded') {
    // Show notification about auto-upgrade
    chrome.notifications.create({
      type: 'basic',
      iconUrl: chrome.runtime.getURL('assets/icons/icon128.png'),
      title: 'Pulse Extension Updated',
      message: `Updated to version ${currentVersion}. ${upgradeResult.changelog}`
    });
  }
}

/**
 * Initialize extension
 */
async function initializeExtension() {
  if (extensionInitialized) {
    return;
  }

  try {
    console.log('Initializing extension...');

    // Initialize storage manager
    await storageManager.init();

    // Initialize consent manager
    const hasConsent = await consentManager.init();
    dataCollectionActive = hasConsent;

    if (!hasConsent) {
      console.log('No valid consent - data collection disabled');
    } else {
      console.log('Valid consent found - data collection enabled');

      // Initialize sync scheduler
      await syncScheduler.init();

      // Set up periodic aggregation
      chrome.alarms.create('aggregateData', {
        periodInMinutes: 60 // Every hour
      });

      // Set up periodic cleanup
      chrome.alarms.create('cleanupData', {
        periodInMinutes: 360 // Every 6 hours
      });
    }

    extensionInitialized = true;
    console.log('Extension initialized successfully');
  } catch (error) {
    console.error('Failed to initialize extension:', error);
  }
}

/**
 * Handle activity events from content scripts
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'activity_event') {
    handleActivityEvent(message.event, sender.tab);
    sendResponse({ success: true });
  } else if (message.type === 'get_consent_status') {
    sendResponse({
      hasConsent: dataCollectionActive,
      consentState: consentManager.getConsentState()
    });
  } else if (message.type === 'grant_consent') {
    consentManager.grantConsent().then(() => {
      dataCollectionActive = true;
      sendResponse({ success: true });
      initializeExtension(); // Re-initialize with consent
    });
    return true; // Keep channel open for async response
  } else if (message.type === 'revoke_consent') {
    consentManager.revokeConsent(message.deleteData).then(() => {
      dataCollectionActive = false;
      sendResponse({ success: true });
    });
    return true;
  } else if (message.type === 'trigger_sync') {
    syncScheduler.triggerManualSync().then(() => {
      sendResponse({ success: true });
    });
    return true;
  } else if (message.type === 'export_data') {
    consentManager.exportUserData().then((success) => {
      sendResponse({ success });
    });
    return true;
  }

  return false;
});

/**
 * Handle activity events
 */
async function handleActivityEvent(event, tab) {
  if (!dataCollectionActive) {
    return;
  }

  try {
    // Add tab information
    if (tab) {
      event.tab_id = tab.id;
      event.window_id = tab.windowId;
    }

    // Store event
    await storageManager.addActivityEvent(event);

    console.debug('Activity event stored:', event.event_type);
  } catch (error) {
    console.error('Failed to handle activity event:', error);
  }
}

/**
 * Track tab activations
 */
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  if (!dataCollectionActive) return;

  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);

    await storageManager.addActivityEvent({
      event_type: 'tab_activated',
      tab_id: activeInfo.tabId,
      window_id: activeInfo.windowId,
      url: tab.url,
      title: tab.title,
      timestamp: Date.now()
    });
  } catch (error) {
    console.error('Failed to track tab activation:', error);
  }
});

/**
 * Track tab updates (URL changes)
 */
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (!dataCollectionActive) return;

  // Only track complete loads with URL changes
  if (changeInfo.status === 'complete' && changeInfo.url) {
    try {
      await storageManager.addActivityEvent({
        event_type: 'tab_updated',
        tab_id: tabId,
        window_id: tab.windowId,
        url: tab.url,
        title: tab.title,
        timestamp: Date.now()
      });
    } catch (error) {
      console.error('Failed to track tab update:', error);
    }
  }
});

/**
 * Track window focus changes
 */
chrome.windows.onFocusChanged.addListener(async (windowId) => {
  if (!dataCollectionActive) return;

  try {
    await storageManager.addActivityEvent({
      event_type: 'window_focus_changed',
      window_id: windowId,
      timestamp: Date.now()
    });
  } catch (error) {
    console.error('Failed to track window focus:', error);
  }
});

/**
 * Track idle state
 */
chrome.idle.setDetectionInterval(300); // 5 minutes

chrome.idle.onStateChanged.addListener(async (newState) => {
  if (!dataCollectionActive) return;

  try {
    await storageManager.addActivityEvent({
      event_type: 'idle_state_changed',
      idle_state: newState, // 'active', 'idle', or 'locked'
      timestamp: Date.now()
    });
  } catch (error) {
    console.error('Failed to track idle state:', error);
  }
});

/**
 * Handle alarms (periodic tasks)
 */
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'aggregateData') {
    await aggregateData();
  } else if (alarm.name === 'cleanupData') {
    await cleanupData();
  }
});

/**
 * Aggregate raw events into hourly sessions
 */
async function aggregateData() {
  if (!dataCollectionActive) return;

  try {
    console.log('Aggregating activity data...');

    // Get events from the last hour
    const oneHourAgo = Date.now() - (60 * 60 * 1000);
    const events = await storageManager.getActivityEvents(oneHourAgo);

    if (events.length === 0) {
      console.log('No events to aggregate');
      return;
    }

    // Aggregate into sessions
    const sessions = await aggregator.aggregateEvents(events);

    // Store aggregated sessions
    for (const session of sessions) {
      await storageManager.addAggregatedSession(session);
    }

    console.log(`Aggregated ${events.length} events into ${sessions.length} sessions`);

    // Trigger sync after aggregation
    await syncScheduler.syncData();
  } catch (error) {
    console.error('Failed to aggregate data:', error);
  }
}

/**
 * Clean up old data
 */
async function cleanupData() {
  try {
    console.log('Cleaning up old data...');
    await storageManager.cleanup();
    console.log('Cleanup complete');
  } catch (error) {
    console.error('Failed to cleanup data:', error);
  }
}

/**
 * Handle extension uninstall (for cleanup tracking)
 */
chrome.runtime.setUninstallURL('https://pulse-feedback-form.example.com');

console.log('Service worker loaded');
