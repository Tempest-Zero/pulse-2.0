# Pulse Extension Guidelines

> Chrome/Firefox extension patterns for Manifest V3 activity tracking.

## Purpose

Provides guidance for working with the browser extension: service worker, content scripts, popup, and backend sync.

## When to Use

- [ ] Modifying the service worker in `background/`
- [ ] Updating content scripts in `content/`
- [ ] Working with popup or options UI
- [ ] Configuring backend sync in `lib/sync-scheduler.js`
- [ ] Updating manifest permissions

## Quick Rules

### Project Structure
```
pulse-extension/
├── manifest.json           # MV3 manifest (permissions, scripts)
├── background/
│   └── service-worker.js   # Main background logic
├── content/
│   └── activity-tracker.js # Injected into pages
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
├── options/
│   ├── options.html
│   ├── options.js
│   └── options.css
├── lib/
│   ├── sync-scheduler.js   # Backend sync (ENDPOINT HERE)
│   ├── storage-manager.js
│   ├── consent-manager.js
│   └── category-db.js
└── assets/                 # Icons
```

### Loading Unpacked

**Chrome:**
1. Navigate to `chrome://extensions`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select `pulse-extension/` folder

**Firefox:**
1. Navigate to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on..."
3. Select `manifest.json`

### Backend Endpoint

**Location**: `lib/sync-scheduler.js` line 12

```javascript
const SYNC_CONFIG = {
    API_ENDPOINT: 'https://back-end-304.up.railway.app/api/v1/extension'
};
```

### Switching Environments

For local development:
```javascript
// Change line 12 in sync-scheduler.js
API_ENDPOINT: 'http://localhost:8000/api/v1/extension'
```

⚠️ **WARNING**: Don't commit localhost URLs!

## Manifest V3 Notes

- Uses `service_worker` (NOT `background.scripts`)
- Service worker terminates after ~30s idle
- Use `chrome.alarms` for scheduled tasks (not setInterval)
- State doesn't persist—use `chrome.storage.local`

## Common Gotchas

| Issue | Cause | Fix |
|-------|-------|-----|
| Sync fails silently | Localhost hardcoded | Check sync-scheduler.js line 12 |
| Service worker dies | MV3 lifecycle | Use chrome.alarms for periodic tasks |
| Storage full | Too much cached data | Implement cleanup in storage-manager.js |
| No consent | User hasn't opted in | Check consent-manager.js state |
| CORS error | Extension origin not allowed | Backend already configured for extensions |

## Key Files

| File | Purpose |
|------|---------|
| `manifest.json` | Extension config (permissions, content scripts) |
| `lib/sync-scheduler.js` | Backend sync with exponential backoff |
| `lib/consent-manager.js` | User consent for data collection |
| `lib/storage-manager.js` | chrome.storage.local wrapper |
| `lib/category-db.js` | Website categorization database |
