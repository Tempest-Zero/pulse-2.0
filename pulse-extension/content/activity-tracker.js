/**
 * Activity Tracker Content Script
 * Monitors user activity on web pages and sends events to background worker
 */

(function() {
  'use strict';

  // Track page visibility and focus
  let pageVisible = !document.hidden;
  let pageFocused = document.hasFocus();
  let lastActivityTime = Date.now();
  let sessionStartTime = Date.now();

  /**
   * Send activity event to background worker
   */
  function sendActivityEvent(eventType, data = {}) {
    chrome.runtime.sendMessage({
      type: 'activity_event',
      event: {
        event_type: eventType,
        url: window.location.href,
        title: document.title,
        timestamp: Date.now(),
        ...data
      }
    }).catch(error => {
      // Extension context may be invalidated, ignore
      console.debug('Failed to send activity event:', error);
    });
  }

  /**
   * Track page visibility changes
   */
  document.addEventListener('visibilitychange', () => {
    const wasVisible = pageVisible;
    pageVisible = !document.hidden;

    if (pageVisible && !wasVisible) {
      // Page became visible
      sendActivityEvent('page_visible', {
        duration_hidden: Date.now() - lastActivityTime
      });
      lastActivityTime = Date.now();
    } else if (!pageVisible && wasVisible) {
      // Page became hidden
      sendActivityEvent('page_hidden', {
        duration_visible: Date.now() - lastActivityTime
      });
      lastActivityTime = Date.now();
    }
  });

  /**
   * Track window focus changes
   */
  window.addEventListener('focus', () => {
    if (!pageFocused) {
      pageFocused = true;
      sendActivityEvent('window_focused', {
        duration_blurred: Date.now() - lastActivityTime
      });
      lastActivityTime = Date.now();
    }
  });

  window.addEventListener('blur', () => {
    if (pageFocused) {
      pageFocused = false;
      sendActivityEvent('window_blurred', {
        duration_focused: Date.now() - lastActivityTime
      });
      lastActivityTime = Date.now();
    }
  });

  /**
   * Track user interactions (for activity detection)
   */
  let interactionTimeout = null;

  function trackInteraction(eventType) {
    // Debounce interactions to avoid spam
    if (interactionTimeout) {
      clearTimeout(interactionTimeout);
    }

    interactionTimeout = setTimeout(() => {
      sendActivityEvent('user_interaction', {
        interaction_type: eventType,
        time_since_last: Date.now() - lastActivityTime
      });
      lastActivityTime = Date.now();
    }, 1000); // 1 second debounce
  }

  // Track clicks
  document.addEventListener('click', () => trackInteraction('click'), { passive: true });

  // Track scrolling
  let scrollTimeout = null;
  document.addEventListener('scroll', () => {
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }
    scrollTimeout = setTimeout(() => {
      trackInteraction('scroll');
    }, 500);
  }, { passive: true });

  // Track keyboard activity (no keylogging - just presence detection)
  let keyTimeout = null;
  document.addEventListener('keydown', () => {
    if (keyTimeout) {
      clearTimeout(keyTimeout);
    }
    keyTimeout = setTimeout(() => {
      trackInteraction('keyboard');
    }, 1000);
  }, { passive: true });

  /**
   * Detect idle state (no interaction for 5 minutes)
   */
  let idleCheckInterval = null;
  const IDLE_THRESHOLD = 5 * 60 * 1000; // 5 minutes

  function checkIdleState() {
    const timeSinceLastActivity = Date.now() - lastActivityTime;

    if (timeSinceLastActivity > IDLE_THRESHOLD && pageVisible) {
      sendActivityEvent('idle_detected', {
        idle_duration: timeSinceLastActivity
      });
    }
  }

  // Check for idle state every minute
  idleCheckInterval = setInterval(checkIdleState, 60 * 1000);

  /**
   * Track session duration when page unloads
   */
  window.addEventListener('beforeunload', () => {
    const sessionDuration = Date.now() - sessionStartTime;

    sendActivityEvent('page_unload', {
      session_duration: sessionDuration,
      total_visible_time: pageVisible ? sessionDuration : 0
    });
  });

  /**
   * Initial page load event
   */
  sendActivityEvent('page_load', {
    referrer: document.referrer || 'direct',
    is_visible: pageVisible,
    is_focused: pageFocused
  });

  /**
   * Track URL changes in Single Page Applications (SPAs)
   */
  let lastUrl = window.location.href;

  function checkUrlChange() {
    const currentUrl = window.location.href;

    if (currentUrl !== lastUrl) {
      sendActivityEvent('url_changed', {
        previous_url: lastUrl,
        new_url: currentUrl,
        change_type: 'spa_navigation'
      });

      lastUrl = currentUrl;
    }
  }

  // Use MutationObserver to detect URL changes (for SPAs)
  const observer = new MutationObserver(checkUrlChange);
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Also use History API listeners
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;

  history.pushState = function() {
    originalPushState.apply(this, arguments);
    checkUrlChange();
  };

  history.replaceState = function() {
    originalReplaceState.apply(this, arguments);
    checkUrlChange();
  };

  window.addEventListener('popstate', checkUrlChange);

  /**
   * Privacy filter - strip sensitive data from URLs
   */
  function stripSensitiveData(url) {
    try {
      const urlObj = new URL(url);

      // Remove query parameters that might contain sensitive data
      const sensitiveParams = ['token', 'key', 'password', 'secret', 'auth', 'session'];

      for (const param of sensitiveParams) {
        urlObj.searchParams.delete(param);
      }

      return urlObj.toString();
    } catch (error) {
      return url;
    }
  }

  /**
   * Listen for messages from background worker
   */
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'get_page_info') {
      // Send current page information
      sendResponse({
        url: window.location.href,
        title: document.title,
        visible: pageVisible,
        focused: pageFocused,
        sessionDuration: Date.now() - sessionStartTime
      });
    }

    return true; // Keep message channel open
  });

  console.debug('Pulse activity tracker initialized');
})();
