import { apiRequest } from './config';

/**
 * Mood API Service
 */

// Map frontend mood values to backend mood values
const MOOD_MAPPING = {
  'energized': 'energized',
  'good': 'calm',
  'neutral': 'calm',
  'low': 'tired',
  'exhausted': 'tired',
  'calm': 'calm',
  'focused': 'focused',
  'tired': 'tired',
};

// Reverse mapping for display
const MOOD_DISPLAY = {
  'energized': { emoji: '🔥', label: 'On fire', value: 'energized' },
  'calm': { emoji: '😊', label: 'Vibing', value: 'good' },
  'focused': { emoji: '🎯', label: 'Focused', value: 'focused' },
  'tired': { emoji: '😓', label: 'Struggling', value: 'low' },
};

export async function getCurrentMood() {
  return apiRequest('/mood/current');
}

export async function setMood(moodValue) {
  // Map frontend mood to backend mood
  const backendMood = MOOD_MAPPING[moodValue] || 'calm';
  return apiRequest('/mood', {
    method: 'POST',
    body: JSON.stringify({ mood: backendMood }),
  });
}

export async function getMoodHistory(limit = 100) {
  return apiRequest(`/mood/history?limit=${limit}`);
}

export async function getMoodCounts(limit = 100) {
  return apiRequest(`/mood/analytics/counts?limit=${limit}`);
}

export async function getMostCommonMood(limit = 100) {
  return apiRequest(`/mood/analytics/most-common?limit=${limit}`);
}

export async function deleteMoodEntry(entryId) {
  return apiRequest(`/mood/${entryId}`, {
    method: 'DELETE',
  });
}

export function mapMoodToBackend(frontendMood) {
  return MOOD_MAPPING[frontendMood] || 'calm';
}

export function mapMoodFromBackend(backendMood) {
  // Find the frontend mood that maps to this backend mood
  for (const [frontend, backend] of Object.entries(MOOD_MAPPING)) {
    if (backend === backendMood) {
      return frontend;
    }
  }
  return 'neutral';
}

