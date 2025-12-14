/**
 * IndexedDB Storage Manager
 * Handles local storage of activity data with retention policies and quota management
 */

const DB_NAME = 'PulseExtensionDB';
const DB_VERSION = 1;
const MAX_STORAGE_MB = 50;

// Store definitions
const STORES = {
  ACTIVITY_EVENTS: 'activity_events',      // Raw events (24h retention)
  AGGREGATED_SESSIONS: 'aggregated_sessions', // Hourly aggregates (7d retention)
  SYNC_QUEUE: 'sync_queue',                // Failed syncs (max 100 entries)
};

class StorageManager {
  constructor() {
    this.db = null;
  }

  /**
   * Initialize the IndexedDB database
   */
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Activity Events Store (raw events)
        if (!db.objectStoreNames.contains(STORES.ACTIVITY_EVENTS)) {
          const activityStore = db.createObjectStore(STORES.ACTIVITY_EVENTS, {
            keyPath: 'id',
            autoIncrement: true
          });
          activityStore.createIndex('timestamp', 'timestamp', { unique: false });
          activityStore.createIndex('event_type', 'event_type', { unique: false });
        }

        // Aggregated Sessions Store (hourly aggregates)
        if (!db.objectStoreNames.contains(STORES.AGGREGATED_SESSIONS)) {
          const sessionStore = db.createObjectStore(STORES.AGGREGATED_SESSIONS, {
            keyPath: 'session_id'
          });
          sessionStore.createIndex('timestamp', 'timestamp', { unique: false });
          sessionStore.createIndex('synced', 'synced', { unique: false });
        }

        // Sync Queue Store (failed syncs)
        if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
          const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, {
            keyPath: 'id',
            autoIncrement: true
          });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
          syncStore.createIndex('retry_count', 'retry_count', { unique: false });
        }
      };
    });
  }

  /**
   * Add an activity event
   */
  async addActivityEvent(event) {
    const transaction = this.db.transaction([STORES.ACTIVITY_EVENTS], 'readwrite');
    const store = transaction.objectStore(STORES.ACTIVITY_EVENTS);

    const eventData = {
      ...event,
      timestamp: Date.now()
    };

    return new Promise((resolve, reject) => {
      const request = store.add(eventData);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Add an aggregated session
   */
  async addAggregatedSession(session) {
    const transaction = this.db.transaction([STORES.AGGREGATED_SESSIONS], 'readwrite');
    const store = transaction.objectStore(STORES.AGGREGATED_SESSIONS);

    return new Promise((resolve, reject) => {
      const request = store.add(session);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all unsynced sessions
   */
  async getUnsyncedSessions() {
    const transaction = this.db.transaction([STORES.AGGREGATED_SESSIONS], 'readonly');
    const store = transaction.objectStore(STORES.AGGREGATED_SESSIONS);
    const index = store.index('synced');

    return new Promise((resolve, reject) => {
      const request = index.getAll(false);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Mark session as synced
   */
  async markSessionSynced(sessionId) {
    const transaction = this.db.transaction([STORES.AGGREGATED_SESSIONS], 'readwrite');
    const store = transaction.objectStore(STORES.AGGREGATED_SESSIONS);

    return new Promise((resolve, reject) => {
      const getRequest = store.get(sessionId);

      getRequest.onsuccess = () => {
        const session = getRequest.result;
        if (session) {
          session.synced = true;
          session.synced_at = Date.now();
          const updateRequest = store.put(session);
          updateRequest.onsuccess = () => resolve();
          updateRequest.onerror = () => reject(updateRequest.error);
        } else {
          resolve(); // Session not found, already deleted
        }
      };

      getRequest.onerror = () => reject(getRequest.error);
    });
  }

  /**
   * Add to sync queue (for failed syncs)
   */
  async addToSyncQueue(data) {
    const transaction = this.db.transaction([STORES.SYNC_QUEUE], 'readwrite');
    const store = transaction.objectStore(STORES.SYNC_QUEUE);

    const queueItem = {
      ...data,
      timestamp: Date.now(),
      retry_count: 0
    };

    return new Promise((resolve, reject) => {
      const request = store.add(queueItem);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get sync queue items
   */
  async getSyncQueue(limit = 100) {
    const transaction = this.db.transaction([STORES.SYNC_QUEUE], 'readonly');
    const store = transaction.objectStore(STORES.SYNC_QUEUE);
    const index = store.index('timestamp');

    return new Promise((resolve, reject) => {
      const request = index.openCursor();
      const results = [];

      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor && results.length < limit) {
          results.push(cursor.value);
          cursor.continue();
        } else {
          resolve(results);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Remove from sync queue
   */
  async removeFromSyncQueue(id) {
    const transaction = this.db.transaction([STORES.SYNC_QUEUE], 'readwrite');
    const store = transaction.objectStore(STORES.SYNC_QUEUE);

    return new Promise((resolve, reject) => {
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Clean up old data based on retention policies
   * - Raw events: 24 hours
   * - Aggregated sessions: 7 days
   * - Sync queue: max 100 entries (oldest dropped)
   */
  async cleanup() {
    const now = Date.now();
    const oneDayAgo = now - (24 * 60 * 60 * 1000);
    const sevenDaysAgo = now - (7 * 24 * 60 * 60 * 1000);

    // Clean up activity events older than 24 hours
    await this._cleanupStore(STORES.ACTIVITY_EVENTS, oneDayAgo);

    // Clean up aggregated sessions older than 7 days (only synced ones)
    await this._cleanupSyncedSessions(sevenDaysAgo);

    // Limit sync queue to 100 entries
    await this._limitSyncQueue(100);
  }

  async _cleanupStore(storeName, maxAge) {
    const transaction = this.db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const index = store.index('timestamp');

    return new Promise((resolve, reject) => {
      const request = index.openCursor(IDBKeyRange.upperBound(maxAge));
      let deleteCount = 0;

      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          cursor.delete();
          deleteCount++;
          cursor.continue();
        } else {
          console.log(`Cleaned up ${deleteCount} old records from ${storeName}`);
          resolve(deleteCount);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }

  async _cleanupSyncedSessions(maxAge) {
    const transaction = this.db.transaction([STORES.AGGREGATED_SESSIONS], 'readwrite');
    const store = transaction.objectStore(STORES.AGGREGATED_SESSIONS);
    const index = store.index('timestamp');

    return new Promise((resolve, reject) => {
      const request = index.openCursor(IDBKeyRange.upperBound(maxAge));
      let deleteCount = 0;

      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          // Only delete if synced
          if (cursor.value.synced) {
            cursor.delete();
            deleteCount++;
          }
          cursor.continue();
        } else {
          console.log(`Cleaned up ${deleteCount} old synced sessions`);
          resolve(deleteCount);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }

  async _limitSyncQueue(maxEntries) {
    const transaction = this.db.transaction([STORES.SYNC_QUEUE], 'readwrite');
    const store = transaction.objectStore(STORES.SYNC_QUEUE);

    return new Promise((resolve, reject) => {
      const countRequest = store.count();

      countRequest.onsuccess = () => {
        const count = countRequest.result;
        if (count <= maxEntries) {
          resolve(0);
          return;
        }

        const toDelete = count - maxEntries;
        const index = store.index('timestamp');
        const request = index.openCursor();
        let deleteCount = 0;

        request.onsuccess = (event) => {
          const cursor = event.target.result;
          if (cursor && deleteCount < toDelete) {
            cursor.delete();
            deleteCount++;
            cursor.continue();
          } else {
            console.log(`Removed ${deleteCount} oldest entries from sync queue`);
            resolve(deleteCount);
          }
        };

        request.onerror = () => reject(request.error);
      };

      countRequest.onerror = () => reject(countRequest.error);
    });
  }

  /**
   * Get current storage usage estimate
   */
  async getStorageEstimate() {
    if (navigator.storage && navigator.storage.estimate) {
      return await navigator.storage.estimate();
    }
    return null;
  }

  /**
   * Check if storage quota is exceeded
   */
  async isQuotaExceeded() {
    const estimate = await this.getStorageEstimate();
    if (!estimate) return false;

    const usageMB = estimate.usage / (1024 * 1024);
    return usageMB > MAX_STORAGE_MB;
  }

  /**
   * Get all activity events (for aggregation)
   */
  async getActivityEvents(since = 0) {
    const transaction = this.db.transaction([STORES.ACTIVITY_EVENTS], 'readonly');
    const store = transaction.objectStore(STORES.ACTIVITY_EVENTS);
    const index = store.index('timestamp');

    return new Promise((resolve, reject) => {
      const request = index.getAll(IDBKeyRange.lowerBound(since));
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Clear all data (for testing or user request)
   */
  async clearAll() {
    const stores = [
      STORES.ACTIVITY_EVENTS,
      STORES.AGGREGATED_SESSIONS,
      STORES.SYNC_QUEUE
    ];

    for (const storeName of stores) {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      await new Promise((resolve, reject) => {
        const request = store.clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    }
  }
}

// Export singleton instance
const storageManager = new StorageManager();
export default storageManager;
