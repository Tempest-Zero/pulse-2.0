import { apiRequest } from './config';

/**
 * Reflections API Service
 */

export async function getReflections(limit = null) {
  const params = new URLSearchParams();
  if (limit) {
    params.append('limit', limit);
  }
  const query = params.toString();
  return apiRequest(`/reflections${query ? `?${query}` : ''}`);
}

export async function getTodayReflection() {
  return apiRequest('/reflections/today');
}

export async function getReflection(reflectionId) {
  return apiRequest(`/reflections/${reflectionId}`);
}

export async function getReflectionByDate(date) {
  // date should be in YYYY-MM-DD format
  return apiRequest(`/reflections/date/${date}`);
}

export async function createReflection(reflectionData) {
  // Map frontend format to backend format
  const backendData = {
    moodScore: reflectionData.mood || reflectionData.moodScore || 3,
    distractions: reflectionData.distractions || [],
    note: reflectionData.note || reflectionData.reflection || '',
    completedTasks: reflectionData.completedTasks || reflectionData.completed_tasks || 0,
    totalTasks: reflectionData.totalTasks || reflectionData.total_tasks || 0,
  };
  return apiRequest('/reflections', {
    method: 'POST',
    body: JSON.stringify(backendData),
  });
}

export async function updateReflection(reflectionId, reflectionData) {
  const backendData = {};
  if (reflectionData.moodScore || reflectionData.mood !== undefined) {
    backendData.moodScore = reflectionData.moodScore || reflectionData.mood;
  }
  if (reflectionData.distractions) {
    backendData.distractions = reflectionData.distractions;
  }
  if (reflectionData.note || reflectionData.reflection) {
    backendData.note = reflectionData.note || reflectionData.reflection;
  }
  
  return apiRequest(`/reflections/${reflectionId}`, {
    method: 'PATCH',
    body: JSON.stringify(backendData),
  });
}

export async function deleteReflection(reflectionId) {
  return apiRequest(`/reflections/${reflectionId}`, {
    method: 'DELETE',
  });
}

export async function getMoodAverage(days = 7) {
  return apiRequest(`/reflections/analytics/mood-average?days=${days}`);
}

export async function getCommonDistractions(days = 30) {
  return apiRequest(`/reflections/analytics/common-distractions?days=${days}`);
}

/**
 * Transform backend reflection to frontend format
 */
export function transformReflection(backendReflection) {
  return {
    id: backendReflection.id,
    date: backendReflection.date,
    mood: backendReflection.moodScore || backendReflection.mood_score,
    moodScore: backendReflection.moodScore || backendReflection.mood_score,
    distractions: backendReflection.distractions || [],
    note: backendReflection.note || '',
    reflection: backendReflection.note || '',
    completedTasks: backendReflection.completedTasks || backendReflection.completed_tasks,
    totalTasks: backendReflection.totalTasks || backendReflection.total_tasks,
  };
}

