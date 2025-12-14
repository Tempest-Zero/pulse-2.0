# Pulse 2.0 Browser Extension

AI-powered productivity companion that learns your work patterns and recommends personalized tasks.

## Features

- **Activity Tracking**: Monitors browsing patterns while respecting privacy
- **Smart Categorization**: 3-tier classification system for websites
- **AI Recommendations**: Deep Q-Network for personalized task suggestions
- **Privacy-First**: Local-first storage with optional cloud sync
- **GDPR/CCPA Compliant**: Versioned consent management

## Installation

### Development Mode

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked"
4. Select the `pulse-extension` directory

### Firefox

1. Navigate to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select the `manifest.json` file

## Architecture

### Directory Structure

```
pulse-extension/
├── manifest.json           # Extension manifest (V3)
├── background/
│   └── service-worker.js  # Background processing
├── content/
│   └── activity-tracker.js # Activity monitoring
├── lib/
│   ├── storage-manager.js  # IndexedDB operations
│   ├── category-db.js      # Website categorization
│   ├── consent-manager.js  # Consent management
│   ├── aggregator.js       # Data aggregation
│   └── sync-scheduler.js   # Cloud synchronization
├── popup/
│   ├── popup.html         # Extension popup
│   ├── popup.css
│   └── popup.js
├── options/
│   ├── options.html       # Settings page
│   ├── options.css
│   └── options.js
└── assets/
    └── icons/             # Extension icons
```

### Key Components

#### Storage Manager
- IndexedDB for local storage
- 24-hour retention for raw events
- 7-day retention for aggregated sessions
- Automatic cleanup and quota management

#### Category Database
- **Tier 1**: Curated 500+ domains (confidence: 1.0)
- **Tier 2**: Heuristic rules (confidence: 0.6-0.9)
- **Tier 3**: User overrides (confidence: 1.0)

#### Consent Manager
- Versioned consent tracking
- Re-consent flow for major updates
- GDPR data export/deletion
- Privacy transparency

#### Sync Scheduler
- Hourly automatic sync
- Exponential backoff retry (30s to 1h)
- Max 10 attempts per session
- Offline queue management

## Privacy & Data Collection

### What We Collect
- Website categories (not full URLs)
- Time spent per category
- Tab switching patterns
- Focus duration metrics

### What We DON'T Collect
- Full browsing history
- Keystrokes or form inputs
- Personal information
- Passwords or credentials

### Data Retention
- **Local**: 7 days (raw events: 24h)
- **Server**: 90 days (anonymized after 30 days)
- **Aggregated**: Indefinite (fully anonymized)

## Development

### Prerequisites
- Chrome 88+ or Firefox 89+
- Pulse backend running on `localhost:8000`

### Testing
```bash
# Load extension in development mode
# Changes to content scripts require page reload
# Changes to background script require extension reload
```

### Building for Production
```bash
# TODO: Add build script for production
```

## API Integration

The extension communicates with the Pulse backend via:
- **Endpoint**: `http://localhost:8000/api/v1/extension`
- **Auth**: JWT Bearer token
- **Versioning**: `X-Extension-Version` header

## Support

For issues or questions:
- GitHub: [pulse-2.0 issues](https://github.com/your-org/pulse-2.0/issues)
- Documentation: [Pulse Docs](https://pulse-docs.example.com)

## License

[Your License Here]
