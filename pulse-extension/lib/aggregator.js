/**
 * Data Aggregator
 * Converts raw activity events into hourly aggregated sessions
 */

import categoryDB from './category-db.js';

class Aggregator {
  constructor() {
    this.currentSession = null;
  }

  /**
   * Aggregate events into hourly sessions
   */
  async aggregateEvents(events) {
    if (!events || events.length === 0) {
      return [];
    }

    // Group events by hour
    const hourlyGroups = this.groupByHour(events);

    // Convert each hourly group into an aggregated session
    const sessions = [];
    for (const [hourKey, hourEvents] of Object.entries(hourlyGroups)) {
      const session = this.createSessionFromEvents(hourKey, hourEvents);
      sessions.push(session);
    }

    return sessions;
  }

  /**
   * Group events by hour
   */
  groupByHour(events) {
    const groups = {};

    for (const event of events) {
      const hourKey = this.getHourKey(event.timestamp);

      if (!groups[hourKey]) {
        groups[hourKey] = [];
      }

      groups[hourKey].push(event);
    }

    return groups;
  }

  /**
   * Get hour key from timestamp (e.g., "2025-01-15T14")
   */
  getHourKey(timestamp) {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');

    return `${year}-${month}-${day}T${hour}`;
  }

  /**
   * Create aggregated session from events
   */
  createSessionFromEvents(hourKey, events) {
    const startTime = new Date(hourKey).getTime();
    const endTime = startTime + (60 * 60 * 1000); // +1 hour

    // Calculate category time distribution
    const categoryTime = this.calculateCategoryTime(events);

    // Calculate behavioral metrics
    const metrics = this.calculateMetrics(events);

    // Generate unique session ID
    const sessionId = `session_${hourKey}_${Date.now()}`;

    return {
      session_id: sessionId,
      timestamp: startTime,
      hour: hourKey,
      duration_minutes: 60,
      category_distribution: categoryTime,
      metrics,
      event_count: events.length,
      synced: false,
      created_at: Date.now()
    };
  }

  /**
   * Calculate time spent per category
   */
  calculateCategoryTime(events) {
    const categoryTime = {
      work: 0,
      leisure: 0,
      social: 0,
      neutral: 0
    };

    let lastEvent = null;
    let lastCategory = null;

    for (const event of events.sort((a, b) => a.timestamp - b.timestamp)) {
      if (event.event_type === 'tab_activated' || event.event_type === 'tab_updated') {
        // Calculate time since last event
        if (lastEvent && lastCategory) {
          const duration = event.timestamp - lastEvent.timestamp;
          // Cap at 10 minutes to avoid idle time inflation
          const cappedDuration = Math.min(duration, 10 * 60 * 1000);
          categoryTime[lastCategory] += cappedDuration;
        }

        // Categorize current URL
        if (event.url) {
          const categoryInfo = categoryDB.categorizeUrl(event.url);
          lastCategory = categoryInfo.category;
        }

        lastEvent = event;
      }
    }

    // Convert milliseconds to minutes
    for (const category in categoryTime) {
      categoryTime[category] = Math.round(categoryTime[category] / (60 * 1000));
    }

    return categoryTime;
  }

  /**
   * Calculate behavioral metrics
   */
  calculateMetrics(events) {
    const tabSwitches = events.filter(e => e.event_type === 'tab_activated').length;
    const windowFocusChanges = events.filter(e => e.event_type === 'window_focus_changed').length;

    // Calculate focus duration (time without switches)
    const focusDurations = this.calculateFocusDurations(events);
    const avgFocusDuration = focusDurations.length > 0
      ? focusDurations.reduce((a, b) => a + b, 0) / focusDurations.length
      : 0;

    // Calculate distraction rate (switches per hour)
    const sessionDuration = 60; // minutes
    const distractionRate = (tabSwitches / sessionDuration) * 60; // Per hour

    return {
      tab_switches: tabSwitches,
      window_focus_changes: windowFocusChanges,
      avg_focus_duration_minutes: Math.round(avgFocusDuration),
      distraction_rate_per_hour: Math.round(distractionRate * 10) / 10, // 1 decimal
      unique_domains: this.countUniqueDomains(events)
    };
  }

  /**
   * Calculate focus durations (time between tab switches)
   */
  calculateFocusDurations(events) {
    const durations = [];
    const activationEvents = events
      .filter(e => e.event_type === 'tab_activated')
      .sort((a, b) => a.timestamp - b.timestamp);

    for (let i = 1; i < activationEvents.length; i++) {
      const duration = activationEvents[i].timestamp - activationEvents[i - 1].timestamp;
      // Cap at 30 minutes to avoid idle time
      const cappedDuration = Math.min(duration, 30 * 60 * 1000);
      durations.push(cappedDuration / (60 * 1000)); // Convert to minutes
    }

    return durations;
  }

  /**
   * Count unique domains visited
   */
  countUniqueDomains(events) {
    const domains = new Set();

    for (const event of events) {
      if (event.url) {
        try {
          const url = new URL(event.url);
          domains.add(url.hostname);
        } catch (error) {
          // Invalid URL, skip
        }
      }
    }

    return domains.size;
  }

  /**
   * Create real-time feature vector for DQN
   * (Continuous features for the AI model)
   */
  createFeatureVector(session, currentTime = Date.now()) {
    const date = new Date(currentTime);

    // Time features (cyclical encoding)
    const hour = date.getHours();
    const timeOfDayNorm = hour / 24;
    const timeOfDaySin = Math.sin(2 * Math.PI * timeOfDayNorm);
    const timeOfDayCos = Math.cos(2 * Math.PI * timeOfDayNorm);

    const dayOfWeek = date.getDay();
    const dayOfWeekNorm = dayOfWeek / 7;

    // Work-life balance ratio
    const workTime = session.category_distribution.work || 0;
    const leisureTime = session.category_distribution.leisure || 0;
    const totalTime = workTime + leisureTime + session.category_distribution.social + session.category_distribution.neutral;
    const workRatio = totalTime > 0 ? workTime / totalTime : 0;

    // Focus metrics (normalized)
    const focusScore = Math.min(session.metrics.avg_focus_duration_minutes / 30, 1.0); // 30 min = perfect focus
    const distractionRate = Math.min(session.metrics.distraction_rate_per_hour / 60, 1.0); // 60/hour = max distraction

    // Session duration (log-normalized)
    const sessionDurationNorm = Math.log(session.duration_minutes + 1) / Math.log(120); // 120 min max

    return {
      time_of_day_sin: timeOfDaySin,
      time_of_day_cos: timeOfDayCos,
      day_of_week: dayOfWeekNorm,
      work_ratio: workRatio,
      focus_score: focusScore,
      distraction_rate: distractionRate,
      session_duration: sessionDurationNorm,
      tab_switches_norm: Math.min(session.metrics.tab_switches / 50, 1.0),
      unique_domains_norm: Math.min(session.metrics.unique_domains / 20, 1.0),

      // Additional context
      is_weekday: dayOfWeek >= 1 && dayOfWeek <= 5 ? 1.0 : 0.0,
      is_working_hours: hour >= 9 && hour <= 17 ? 1.0 : 0.0,
      workload_pressure: this.estimateWorkloadPressure(session)
    };
  }

  /**
   * Estimate workload pressure based on activity patterns
   */
  estimateWorkloadPressure(session) {
    // High tab switches + high work time = high pressure
    const workRatio = session.category_distribution.work / 60; // Normalized to hour
    const switchRate = session.metrics.tab_switches / 60;

    return Math.min((workRatio * 0.6) + (switchRate * 0.4), 1.0);
  }

  /**
   * Aggregate current active session (real-time)
   */
  async getCurrentSessionSummary() {
    // This would aggregate the last hour of activity on-demand
    const storageManager = (await import('./storage-manager.js')).default;
    await storageManager.init();

    const oneHourAgo = Date.now() - (60 * 60 * 1000);
    const recentEvents = await storageManager.getActivityEvents(oneHourAgo);

    if (recentEvents.length === 0) {
      return null;
    }

    const hourKey = this.getHourKey(Date.now());
    return this.createSessionFromEvents(hourKey, recentEvents);
  }
}

// Export singleton instance
const aggregator = new Aggregator();
export default aggregator;
