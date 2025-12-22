import { apiRequest } from './config';

/**
 * Feedback API Service
 * Handles user ratings and reviews for the app.
 */

/**
 * Submit new feedback
 * @param {Object} feedbackData - Object containing rating, category, and review
 * @param {number} feedbackData.rating - Rating from 1-5
 * @param {string} feedbackData.category - Category: general, feature, bug, improvement
 * @param {string} feedbackData.review - Optional review text
 */
export async function submitFeedback(feedbackData) {
    return apiRequest('/feedback/', {
        method: 'POST',
        body: JSON.stringify({
            rating: feedbackData.rating,
            category: feedbackData.category || 'general',
            review: feedbackData.review || null,
        }),
    });
}

/**
 * Get current user's feedback history
 * @param {number} limit - Maximum number of feedback entries to return
 */
export async function getUserFeedback(limit = 10) {
    return apiRequest(`/feedback/?limit=${limit}`);
}

/**
 * Get feedback statistics
 */
export async function getFeedbackStats() {
    return apiRequest('/feedback/stats');
}

/**
 * Delete a feedback entry
 * @param {number} feedbackId - ID of the feedback to delete
 */
export async function deleteFeedback(feedbackId) {
    return apiRequest(`/feedback/${feedbackId}`, {
        method: 'DELETE',
    });
}
