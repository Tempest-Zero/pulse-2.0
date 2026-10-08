# Pulse 2.0 - Your Calm Time Coach

An AI-powered productivity companion that learns your work patterns and recommends personalized tasks at the right time.

## 🎯 Project Overview

Pulse 2.0 is a comprehensive productivity system that combines:
- **Browser Extension**: Tracks browsing patterns while respecting privacy
- **AI Engine**: Deep Q-Network (DQN) for personalized task recommendations
- **Web App**: Beautiful Next.js frontend for task management
- **Backend API**: FastAPI with SQLite for data management

## 🚀 New: Browser Extension

The browser extension enhances Pulse with behavioral insights:

- **Smart Activity Tracking**: Monitors browsing patterns (categories only, not full URLs)
- **3-Tier Category System**: 500+ curated domains + heuristics + user overrides
- **Privacy-First Design**: Local storage, GDPR/CCPA compliant
- **AI-Powered Recommendations**: DQN learns when you're most productive
- **Offline Support**: Works without internet, syncs when online

### Quick Start (Extension)

```bash
# Load extension in Chrome
1. Navigate to chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select pulse-extension/ directory

# Start backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

See [BROWSER_EXTENSION_IMPLEMENTATION.md](./BROWSER_EXTENSION_IMPLEMENTATION.md) for detailed documentation.

## 📦 Project Structure

```
pulse-2.0/
├── backend/              # FastAPI backend
│   ├── ai/              # DQN agent, feature encoder
│   ├── models/          # Database models
│   ├── routers/         # API endpoints
│   ├── crud/            # Database operations
│   └── schema/          # Pydantic schemas
├── frontend/            # Next.js web app
│   └── src/
│       ├── pages/       # App pages
│       └── components/  # React components
├── pulse-extension/     # Browser extension (NEW)
│   ├── background/      # Service worker
│   ├── content/         # Activity tracker
│   ├── lib/             # Core libraries
│   ├── popup/           # Extension popup
│   └── options/         # Settings page
└── docs/                # Documentation
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python 3.10+)
- SQLAlchemy ORM
- SQLite database
- PyTorch (DQN agent)
- Pydantic validation

**Frontend:**
- Next.js 14
- React 18
- Tailwind CSS (planned)

**Extension:**
- Manifest V3
- IndexedDB
- ES6 Modules
- Vanilla JavaScript

## 🏃 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip & npm

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from models.base import init_db; init_db()"

# Run server
uvicorn main:app --reload --port 8000
```

API will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

App will be available at http://localhost:3000

### Extension Setup

See [pulse-extension/README.md](./pulse-extension/README.md) for installation instructions.

## 📊 Features

### Core Functionality
- ✅ Task management (CRUD operations)
- ✅ Daily schedule planning
- ✅ Mood tracking
- ✅ Reflection journaling
- ✅ RESTful API

### Browser Extension (NEW)
- ✅ Activity tracking with privacy filters
- ✅ Website categorization (work/leisure/social)
- ✅ Behavioral metrics (focus, distraction)
- ✅ Consent management (GDPR/CCPA)
- ✅ Offline support with sync
- ✅ Category database (500+ domains)

### AI/ML (NEW)
- ✅ Deep Q-Network (DQN) agent
- ✅ Continuous feature encoding (12 features)
- ✅ Experience replay buffer
- ✅ Personalized task recommendations

### Upcoming
- ⏳ Task recommendation UI integration
- ⏳ Cross-device sync
- ⏳ Analytics dashboard
- ⏳ A/B testing framework

## 🔒 Privacy & Security

Pulse 2.0 is designed with privacy as a core principle:

- **No Full URL Tracking**: Only website categories stored
- **No Keystroke Logging**: Zero keylogger functionality
- **Local-First Storage**: 7-day local retention before sync
- **Automatic Anonymization**: Server data anonymized after 30 days
- **User Control**: Export, view, or delete all data anytime
- **Transparent Consent**: Clear explanation of data collection

## 📖 API Documentation

### Core Endpoints

- `GET /` - Health check
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/schedule` - Get schedule blocks
- `POST /api/moods` - Log mood entry
- `POST /api/reflections` - Create reflection

### Extension Endpoints (NEW)

- `POST /api/v1/extension/sync` - Sync browsing sessions
- `GET /api/v1/extension/version` - Check compatibility
- `GET /api/v1/extension/consent/status` - Get consent status
- `POST /api/v1/extension/consent/grant` - Grant consent
- `POST /api/v1/extension/consent/revoke` - Revoke consent

See [BROWSER_EXTENSION_IMPLEMENTATION.md](./BROWSER_EXTENSION_IMPLEMENTATION.md) for detailed API docs.

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Extension Testing

```bash
# Load extension in developer mode
# Open DevTools console
# Monitor logs and network requests
```

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- DQN implementation inspired by DeepMind's original paper
- Privacy design influenced by GDPR best practices
- Icon design: [Attribution if applicable]


Built with ❤️ for calm, focused productivity
