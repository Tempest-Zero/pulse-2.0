/**
 * Sync Scheduler
 * Handles data synchronization with backend using exponential backoff retry strategy
 */

const SYNC_CONFIG = {
  INITIAL_RETRY_DELAY: 30 * 1000,      // 30 seconds
  MAX_RETRY_DELAY: 60 * 60 * 1000,     // 1 hour
  BACKOFF_MULTIPLIER: 2,
  MAX_ATTEMPTS_PER_SESSION: 10,
  SYNC_INTERVAL: 60 * 60 * 1000,       // 1 hour
  API_ENDPOINT: 'https://back-end-304.up.railway.app/api/v1/extension'
};

class SyncScheduler {
  constructor() {
    this.isSyncing = false;
    this.retryTimeout = null;
    this.currentRetryDelay = SYNC_CONFIG.INITIAL_RETRY_DELAY;
    this.syncAttempts = 0;
  }

  /**
   * Initialize sync scheduler
   */
  async init() {
    // Set up periodic sync alarm
    chrome.alarms.create('periodicSync', {
      periodInMinutes: 60 // Every hour
    });

    // Listen for alarm
    chrome.alarms.onAlarm.addListener((alarm) => {
      if (alarm.name === 'periodicSync') {
        this.syncData();
      }
    });

    // Listen for network status changes
    if (typeof navigator !== 'undefined' && navigator.onLine !== undefined) {
      window.addEventListener('online', () => {
        console.log('Network online - attempting sync');
        this.syncData();
      });
    }

    // Initial sync on startup
    await this.syncData();
  }

  /**
   * Main sync function
   */
  async syncData() {
    // Check if already syncing
    if (this.isSyncing) {
      console.log('Sync already in progress, skipping');
      return;
    }

    // Check if online
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      console.log('Offline - skipping sync');
      return;
    }

    // Check consent
    const consentManager = (await import('./consent-manager.js')).default;
    const hasConsent = await consentManager.isDataCollectionActive();

    if (!hasConsent) {
      console.log('No consent - skipping sync');
      return;
    }

    this.isSyncing = true;

    try {
      // Get unsynced sessions
      const storageManager = (await import('./storage-manager.js')).default;
      await storageManager.init();

      const unsyncedSessions = await storageManager.getUnsyncedSessions();

      if (unsyncedSessions.length === 0) {
        console.log('No unsynced sessions');
        this.isSyncing = false;
        return;
      }

      console.log(`Syncing ${unsyncedSessions.length} sessions...`);

      // Sync sessions
      const result = await this.syncSessions(unsyncedSessions);

      if (result.success) {
        // Mark sessions as synced
        for (const session of unsyncedSessions) {
          await storageManager.markSessionSynced(session.session_id);
        }

        // Reset retry state on success
        this.currentRetryDelay = SYNC_CONFIG.INITIAL_RETRY_DELAY;
        this.syncAttempts = 0;

        console.log(`Successfully synced ${unsyncedSessions.length} sessions`);
      } else {
        // Sync failed - add to retry queue
        await this.handleSyncFailure(unsyncedSessions, result.error);
      }
    } catch (error) {
      console.error('Sync error:', error);
      await this.handleSyncFailure([], error);
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Sync sessions to backend
   */
  async syncSessions(sessions) {
    try {
      // Get auth token (would be implemented with actual auth)
      const authToken = await this.getAuthToken();

      const response = await fetch(`${SYNC_CONFIG.API_ENDPOINT}/sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Extension-Version': chrome.runtime.getManifest().version,
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          sessions,
          timestamp: Date.now()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Handle sync failure with exponential backoff
   */
  async handleSyncFailure(sessions, error) {
    this.syncAttempts++;

    if (this.syncAttempts >= SYNC_CONFIG.MAX_ATTEMPTS_PER_SESSION) {
      console.error('Max sync attempts reached - giving up');
      this.syncAttempts = 0;
      this.currentRetryDelay = SYNC_CONFIG.INITIAL_RETRY_DELAY;

      // Add to sync queue for later manual retry
      const storageManager = (await import('./storage-manager.js')).default;
      await storageManager.init();

      for (const session of sessions) {
        await storageManager.addToSyncQueue({
          type: 'session',
          data: session,
          error: error
        });
      }

      return;
    }

    console.log(`Sync failed (attempt ${this.syncAttempts}/${SYNC_CONFIG.MAX_ATTEMPTS_PER_SESSION})`);
    console.log(`Retrying in ${this.currentRetryDelay / 1000} seconds...`);

    // Schedule retry with exponential backoff
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }

    this.retryTimeout = setTimeout(() => {
      this.syncData();
    }, this.currentRetryDelay);

    // Increase delay for next retry
    this.currentRetryDelay = Math.min(
      this.currentRetryDelay * SYNC_CONFIG.BACKOFF_MULTIPLIER,
      SYNC_CONFIG.MAX_RETRY_DELAY
    );
  }

  /**
   * Get authentication token (placeholder)
   */
  async getAuthToken() {
    // TODO: Implement actual authentication
    // For now, return a placeholder token
    const result = await chrome.storage.local.get('authToken');
    return result.authToken || 'demo-token';
  }

  /**
   * Manual sync trigger (from UI)
   */
  async triggerManualSync() {
    console.log('Manual sync triggered');
    await this.syncData();
  }

  /**
   * Get sync status
   */
  getSyncStatus() {
    return {
      isSyncing: this.isSyncing,
      syncAttempts: this.syncAttempts,
      nextRetryDelay: this.currentRetryDelay,
      isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true
    };
  }

  /**
   * Process sync queue (retry failed syncs)
   */
  async processSyncQueue() {
    const storageManager = (await import('./storage-manager.js')).default;
    await storageManager.init();

    const queueItems = await storageManager.getSyncQueue(10); // Process 10 at a time

    if (queueItems.length === 0) {
      return;
    }

    console.log(`Processing ${queueItems.length} queued sync items...`);

    for (const item of queueItems) {
      try {
        if (item.type === 'session') {
          const result = await this.syncSessions([item.data]);

          if (result.success) {
            await storageManager.removeFromSyncQueue(item.id);
            console.log('Queued session synced successfully');
          }
        }
      } catch (error) {
        console.error('Error processing queue item:', error);
      }
    }
  }

  /**
   * Check for API version compatibility
   */
  async checkApiCompatibility() {
    try {
      const response = await fetch(`${SYNC_CONFIG.API_ENDPOINT}/version`, {
        method: 'GET',
        headers: {
          'X-Extension-Version': chrome.runtime.getManifest().version
        }
      });

      if (!response.ok) {
        return { compatible: false, upgradeRequired: true };
      }

      const data = await response.json();

      return {
        compatible: data.compatible !== false,
        upgradeRequired: data.upgrade_required === true,
        message: data.message
      };
    } catch (error) {
      console.error('Failed to check API compatibility:', error);
      return { compatible: true, upgradeRequired: false }; // Assume compatible on error
    }
  }
}

// Export singleton instance
const syncScheduler = new SyncScheduler();
export default syncScheduler;
