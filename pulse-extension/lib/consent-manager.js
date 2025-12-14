/**
 * Consent Manager
 * Handles consent versioning, state management, and GDPR/CCPA compliance
 */

const CONSENT_VERSIONS = {
  '1.0.0': {
    version: '1.0.0',
    effectiveDate: '2025-01-01',
    changelog: 'Initial release: Basic activity tracking and task recommendations',
    requiresReconsent: false,
    dataRetentionPolicy: 'keep',
    features: [
      'Tab activity tracking',
      'Time-of-day patterns',
      'Basic task recommendations',
      'Local data storage'
    ]
  },
  '1.1.0': {
    version: '1.1.0',
    effectiveDate: '2025-02-01',
    changelog: 'Added behavioral signals: focus score, distraction rate',
    requiresReconsent: false,
    dataRetentionPolicy: 'keep',
    features: [
      'Tab activity tracking',
      'Time-of-day patterns',
      'Focus score tracking',
      'Distraction rate analysis',
      'Enhanced task recommendations',
      'Local data storage'
    ]
  },
  '2.0.0': {
    version: '2.0.0',
    effectiveDate: '2025-06-01',
    changelog: 'Major update: Cloud sync and AI personalization',
    requiresReconsent: true,
    dataRetentionPolicy: 'anonymize',
    features: [
      'Tab activity tracking',
      'Time-of-day patterns',
      'Focus score tracking',
      'Distraction rate analysis',
      'Cloud synchronization',
      'AI-powered personalization',
      'Cross-device support',
      'Enhanced recommendations'
    ]
  }
};

// Current version
const CURRENT_VERSION = '1.0.0';

class ConsentManager {
  constructor() {
    this.consentState = null;
  }

  /**
   * Initialize consent manager and check consent status
   */
  async init() {
    await this.loadConsentState();

    // Check if re-consent is needed
    if (this.needsReconsent()) {
      await this.pauseDataCollection();
      return false; // Consent not valid
    }

    return this.hasValidConsent();
  }

  /**
   * Load consent state from storage
   */
  async loadConsentState() {
    try {
      const result = await chrome.storage.local.get('consentState');
      this.consentState = result.consentState || null;
    } catch (error) {
      console.error('Failed to load consent state:', error);
      this.consentState = null;
    }
  }

  /**
   * Save consent state to storage
   */
  async saveConsentState() {
    try {
      await chrome.storage.local.set({
        consentState: this.consentState
      });
    } catch (error) {
      console.error('Failed to save consent state:', error);
    }
  }

  /**
   * Grant consent for current version
   */
  async grantConsent() {
    const versionInfo = CONSENT_VERSIONS[CURRENT_VERSION];

    this.consentState = {
      version: CURRENT_VERSION,
      granted: true,
      grantedAt: Date.now(),
      effectiveDate: versionInfo.effectiveDate,
      features: versionInfo.features,
      dataCollectionActive: true
    };

    await this.saveConsentState();
    await this.resumeDataCollection();

    console.log('Consent granted for version:', CURRENT_VERSION);
    return true;
  }

  /**
   * Revoke consent
   */
  async revokeConsent(deleteData = false) {
    if (this.consentState) {
      this.consentState.granted = false;
      this.consentState.revokedAt = Date.now();
      this.consentState.dataCollectionActive = false;
    }

    await this.saveConsentState();
    await this.pauseDataCollection();

    if (deleteData) {
      await this.deleteAllData();
    }

    console.log('Consent revoked');
  }

  /**
   * Check if user has valid consent
   */
  hasValidConsent() {
    if (!this.consentState) return false;
    if (!this.consentState.granted) return false;
    if (this.consentState.version !== CURRENT_VERSION) return false;
    return true;
  }

  /**
   * Check if re-consent is needed
   */
  needsReconsent() {
    if (!this.consentState) return true;
    if (!this.consentState.granted) return false; // Already revoked

    const currentVersionInfo = CONSENT_VERSIONS[CURRENT_VERSION];
    const userVersion = this.consentState.version;

    // If user is on old version and new version requires reconsent
    if (userVersion !== CURRENT_VERSION && currentVersionInfo.requiresReconsent) {
      return true;
    }

    return false;
  }

  /**
   * Get consent version info
   */
  getVersionInfo(version = CURRENT_VERSION) {
    return CONSENT_VERSIONS[version] || null;
  }

  /**
   * Get current consent state
   */
  getConsentState() {
    return this.consentState;
  }

  /**
   * Pause data collection
   */
  async pauseDataCollection() {
    await chrome.storage.local.set({
      dataCollectionPaused: true
    });
    console.log('Data collection paused');
  }

  /**
   * Resume data collection
   */
  async resumeDataCollection() {
    await chrome.storage.local.set({
      dataCollectionPaused: false
    });
    console.log('Data collection resumed');
  }

  /**
   * Check if data collection is active
   */
  async isDataCollectionActive() {
    try {
      const result = await chrome.storage.local.get('dataCollectionPaused');
      return !result.dataCollectionPaused && this.hasValidConsent();
    } catch (error) {
      console.error('Failed to check data collection status:', error);
      return false;
    }
  }

  /**
   * Delete all local data
   */
  async deleteAllData() {
    try {
      // Clear IndexedDB
      const storageManager = (await import('./storage-manager.js')).default;
      await storageManager.init();
      await storageManager.clearAll();

      // Clear chrome.storage (except consent state for record-keeping)
      const keysToRemove = [
        'categoryOverrides',
        'userPreferences',
        'sessionCache'
      ];
      await chrome.storage.local.remove(keysToRemove);

      console.log('All user data deleted');
    } catch (error) {
      console.error('Failed to delete data:', error);
    }
  }

  /**
   * Handle consent version upgrade
   */
  async handleVersionUpgrade(newVersion) {
    const oldVersion = this.consentState?.version || '0.0.0';
    const newVersionInfo = CONSENT_VERSIONS[newVersion];

    console.log(`Upgrading consent from ${oldVersion} to ${newVersion}`);

    if (newVersionInfo.requiresReconsent) {
      // Major version change - requires user action
      await this.pauseDataCollection();
      return {
        action: 'reconsent_required',
        oldVersion,
        newVersion,
        changelog: newVersionInfo.changelog
      };
    } else {
      // Minor version change - auto-upgrade with notification
      if (this.consentState) {
        this.consentState.version = newVersion;
        this.consentState.upgradedAt = Date.now();
        await this.saveConsentState();
      }

      return {
        action: 'auto_upgraded',
        oldVersion,
        newVersion,
        changelog: newVersionInfo.changelog
      };
    }
  }

  /**
   * Get data handling summary for privacy transparency
   */
  getDataHandlingSummary() {
    const versionInfo = this.getVersionInfo();

    return {
      version: CURRENT_VERSION,
      dataCollected: [
        'Tab URLs and titles (categorized only, full URLs not stored)',
        'Time spent on different website categories',
        'Tab switching frequency',
        'Focus duration patterns',
        'Time-of-day preferences'
      ],
      dataNotCollected: [
        'Full browsing history',
        'Keystrokes or form inputs',
        'Personal information from websites',
        'File downloads',
        'Passwords or credentials'
      ],
      retention: {
        local: '7 days',
        server: '90 days (anonymized after 30 days)',
        aggregated: 'Indefinitely (fully anonymized)'
      },
      sharing: 'No data shared with third parties',
      rights: [
        'View all collected data',
        'Export your data',
        'Delete your data',
        'Revoke consent at any time'
      ]
    };
  }

  /**
   * Export user data (GDPR right to data portability)
   */
  async exportUserData() {
    try {
      const storageManager = (await import('./storage-manager.js')).default;
      await storageManager.init();

      const sessions = await storageManager.getUnsyncedSessions();
      const events = await storageManager.getActivityEvents();

      const exportData = {
        exportDate: new Date().toISOString(),
        consentState: this.consentState,
        sessions,
        events,
        version: CURRENT_VERSION
      };

      // Create downloadable JSON file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);

      // Trigger download
      await chrome.downloads.download({
        url,
        filename: `pulse-data-export-${Date.now()}.json`,
        saveAs: true
      });

      console.log('User data exported successfully');
      return true;
    } catch (error) {
      console.error('Failed to export user data:', error);
      return false;
    }
  }
}

// Export singleton instance
const consentManager = new ConsentManager();
export default consentManager;
