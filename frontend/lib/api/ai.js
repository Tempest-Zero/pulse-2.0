import { apiRequest } from './config';

/**
 * AI API Service
 * Handles all AI recommendation endpoints
 */

/**
 * Get an AI-powered task recommendation
 */
export async function getRecommendation(userId = null) {
  const query = userId ? `?user_id=${userId}` : '';
  return apiRequest(`/ai/recommendation${query}`);
}

/**
 * Submit feedback for a recommendation
 */
export async function submitFeedback(feedback) {
  return apiRequest('/ai/feedback', {
    method: 'POST',
    body: JSON.stringify(feedback),
  });
}

/**
 * Get AI agent statistics
 */
export async function getStats(userId = null) {
  const query = userId ? `?user_id=${userId}` : '';
  return apiRequest(`/ai/stats${query}`);
}

/**
 * Get current learning phase information
 */
export async function getPhase(userId = null) {
  const query = userId ? `?user_id=${userId}` : '';
  return apiRequest(`/ai/phase${query}`);
}

/**
 * Trigger batch inference of outcomes for old recommendations
 */
export async function inferFeedbackBatch(minAgeHours = 2, limit = 100) {
  return apiRequest(`/ai/infer-feedback?min_age_hours=${minAgeHours}&limit=${limit}`, {
    method: 'POST',
  });
}

/**
 * Manually trigger agent model persistence
 */
export async function persistAgentModels() {
  return apiRequest('/ai/persist', {
    method: 'POST',
  });
}

/**
 * Break down a complex task into subtasks
 */
export async function breakdownTask(taskId) {
  return apiRequest(`/ai/breakdown-task/${taskId}`, {
    method: 'POST',
  });
}

