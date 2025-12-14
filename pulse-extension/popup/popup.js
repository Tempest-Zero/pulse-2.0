/**
 * Popup UI Controller
 */

// Get DOM elements
const consentRequiredScreen = document.getElementById('consentRequired');
const mainScreen = document.getElementById('mainScreen');
const errorScreen = document.getElementById('errorScreen');

const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

const workTime = document.getElementById('workTime');
const leisureTime = document.getElementById('leisureTime');
const focusScore = document.getElementById('focusScore');
const tabSwitches = document.getElementById('tabSwitches');

const recommendationText = document.getElementById('recommendationText');
const acceptRecommendation = document.getElementById('acceptRecommendation');
const dismissRecommendation = document.getElementById('dismissRecommendation');

const syncNowBtn = document.getElementById('syncNowBtn');
const viewStatsBtn = document.getElementById('viewStatsBtn');
const reviewConsentBtn = document.getElementById('reviewConsentBtn');
const retryBtn = document.getElementById('retryBtn');

const version = document.getElementById('version');
const errorMessage = document.getElementById('errorMessage');

/**
 * Initialize popup
 */
async function init() {
  try {
    // Set version
    version.textContent = `v${chrome.runtime.getManifest().version}`;

    // Check consent status
    const response = await chrome.runtime.sendMessage({ type: 'get_consent_status' });

    if (!response.hasConsent) {
      showScreen('consent');
      updateStatus('warning', 'Consent required');
      return;
    }

    // Load dashboard data
    await loadDashboard();

    showScreen('main');
    updateStatus('active', 'Active');
  } catch (error) {
    console.error('Failed to initialize popup:', error);
    showError('Failed to load extension data');
  }
}

/**
 * Show specific screen
 */
function showScreen(screen) {
  consentRequiredScreen.style.display = 'none';
  mainScreen.style.display = 'none';
  errorScreen.style.display = 'none';

  if (screen === 'consent') {
    consentRequiredScreen.style.display = 'block';
  } else if (screen === 'main') {
    mainScreen.style.display = 'block';
  } else if (screen === 'error') {
    errorScreen.style.display = 'block';
  }
}

/**
 * Update status indicator
 */
function updateStatus(status, text) {
  statusDot.className = 'status-dot ' + status;
  statusText.textContent = text;
}

/**
 * Load dashboard data
 */
async function loadDashboard() {
  try {
    // Get today's activity summary (would come from storage or backend)
    const summary = await getTodaySummary();

    // Update stats
    workTime.textContent = formatTime(summary.workTime);
    leisureTime.textContent = formatTime(summary.leisureTime);
    focusScore.textContent = summary.focusScore + '%';
    tabSwitches.textContent = summary.tabSwitches;

    // Load recommendation
    const recommendation = await getCurrentRecommendation();
    recommendationText.textContent = recommendation.text;
  } catch (error) {
    console.error('Failed to load dashboard:', error);
    throw error;
  }
}

/**
 * Get today's activity summary
 */
async function getTodaySummary() {
  // This would fetch from storage or backend
  // For now, return placeholder data
  return {
    workTime: 120, // minutes
    leisureTime: 45,
    focusScore: 78,
    tabSwitches: 42
  };
}

/**
 * Get current recommendation
 */
async function getCurrentRecommendation() {
  // This would come from the AI backend
  // For now, return placeholder
  const hour = new Date().getHours();

  if (hour < 12) {
    return {
      text: 'Good morning! Start with your most important task while your focus is fresh.',
      taskId: null
    };
  } else if (hour < 17) {
    return {
      text: 'Your focus is high right now. Great time to tackle that complex project task.',
      taskId: null
    };
  } else {
    return {
      text: 'Wind down with some lighter tasks. You\'ve had a productive day!',
      taskId: null
    };
  }
}

/**
 * Format time in minutes to human-readable
 */
function formatTime(minutes) {
  if (minutes < 60) {
    return `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (mins === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${mins}m`;
}

/**
 * Show error screen
 */
function showError(message) {
  errorMessage.textContent = message;
  showScreen('error');
}

/**
 * Event Listeners
 */

// Review consent button
reviewConsentBtn.addEventListener('click', () => {
  chrome.tabs.create({
    url: chrome.runtime.getURL('options/options.html?consent=required')
  });
  window.close();
});

// Accept recommendation
acceptRecommendation.addEventListener('click', async () => {
  // Handle recommendation acceptance
  recommendationText.textContent = 'Great! Opening Pulse dashboard...';

  // Open main Pulse app
  chrome.tabs.create({
    url: 'https://pulse-20-production-314b.up.railway.app' // Pulse frontend URL
  });

  setTimeout(() => window.close(), 500);
});

// Dismiss recommendation
dismissRecommendation.addEventListener('click', async () => {
  recommendationText.textContent = 'Loading next recommendation...';

  // Get next recommendation
  const nextRecommendation = await getCurrentRecommendation();
  recommendationText.textContent = nextRecommendation.text;
});

// Sync now button
syncNowBtn.addEventListener('click', async () => {
  const originalText = syncNowBtn.textContent;
  syncNowBtn.textContent = '⏳ Syncing...';
  syncNowBtn.disabled = true;

  try {
    await chrome.runtime.sendMessage({ type: 'trigger_sync' });

    syncNowBtn.textContent = '✓ Synced';

    setTimeout(() => {
      syncNowBtn.textContent = originalText;
      syncNowBtn.disabled = false;
    }, 2000);
  } catch (error) {
    console.error('Sync failed:', error);
    syncNowBtn.textContent = '✗ Failed';

    setTimeout(() => {
      syncNowBtn.textContent = originalText;
      syncNowBtn.disabled = false;
    }, 2000);
  }
});

// View stats button
viewStatsBtn.addEventListener('click', () => {
  chrome.tabs.create({
    url: 'https://pulse-20-production-314b.up.railway.app/stats' // Pulse stats page
  });
  window.close();
});

// Retry button
retryBtn.addEventListener('click', () => {
  init();
});

// Initialize on load
init();
