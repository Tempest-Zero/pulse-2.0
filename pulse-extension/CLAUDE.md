# CLAUDE.md - Browser Extension

> **Purpose**: Extension-specific structure, loading instructions, and gotchas.

## Folder Structure

```
pulse-extension/
├── manifest.json         # MV3 extension manifest
├── background/
│   └── service-worker.js # Background service worker
├── content/
│   └── activity-tracker.js # Content script (injected into pages)
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
├── options/
│   ├── options.html      # Settings page
│   ├── options.js
│   └── options.css
├── lib/
│   ├── sync-scheduler.js # Backend sync with retry logic
│   ├── storage-manager.js
│   ├── consent-manager.js
│   ├── category-db.js    # Website categorization
│   └── aggregator.js
└── assets/               # Icons (16, 48, 128px)
```

## Loading the Extension

### Chrome

1. Navigate to `chrome://extensions`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `pulse-extension/` folder
5. Extension appears in toolbar

### Firefox

1. Navigate to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on..."
3. Select `pulse-extension/manifest.json`

## Backend Endpoint Configuration

**Location**: `lib/sync-scheduler.js` line 12

```javascript
const SYNC_CONFIG = {
  // ...
  API_ENDPOINT: 'https://back-end-304.up.railway.app/api/v1/extension'
};
```

### Switching to Local Development

For local testing, change to:
```javascript
API_ENDPOINT: 'http://localhost:8000/api/v1/extension'
```

**⚠️ Warning**: Don't commit localhost URLs. Check this before pushing.

## Key Files

| File | Purpose |
|------|---------|
| `manifest.json` | Extension configuration (permissions, scripts) |
| `background/service-worker.js` | Main background logic, alarm handlers |
| `content/activity-tracker.js` | Injected into pages, tracks activity |
| `lib/sync-scheduler.js` | Syncs data to backend with exponential backoff |
| `lib/consent-manager.js` | User consent for data collection |
| `lib/storage-manager.js` | chrome.storage.local wrapper |

## Manifest V3 Notes

- Uses `service_worker` instead of `background.scripts`
- Service worker can be terminated when idle
- Use `chrome.alarms` for periodic tasks (not setInterval)
- State doesn't persist—use `chrome.storage.local`

## Sync Flow

1. `activity-tracker.js` collects browsing data (with consent)
2. Data stored in `chrome.storage.local` via `storage-manager.js`
3. `sync-scheduler.js` periodically syncs to backend
4. Exponential backoff on failures (30s → 1hr max)

## Common Gotchas

### Localhost Hardcoded
- Always check `sync-scheduler.js` before deploying
- Search for `localhost` in the extension folder

### Service Worker Lifecycle
- Worker terminates after ~30 seconds of inactivity
- Use `chrome.alarms` for scheduled tasks
- Don't rely on in-memory state

### Consent Required
- Extension won't collect/sync without user consent
- Consent managed by `consent-manager.js`
- Check options page for consent status

### CORS from Extension
- Extension origins (`chrome-extension://*`) must be in backend CORS
- Already configured in `backend/main.py`

### Testing Sync
1. Open extension popup
2. Check console for sync status
3. Look for "Syncing X sessions..." messages
