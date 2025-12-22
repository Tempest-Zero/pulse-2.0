import { apiRequest, publicApiRequest } from './config';

/**
 * Feedback API Service
 * Handles user ratings and reviews for the app.
 */

/**
 * Submit new feedback (requires authentication)
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
 * Get all feedback from all users (public - no auth required)
 * @param {number} limit - Maximum number of feedback entries to return
 */
export async function getAllFeedback(limit = 50) {
    return publicApiRequest(`/feedback/all?limit=${limit}`);
}

/**
 * Get current user's feedback history (requires auth)
 * @param {number} limit - Maximum number of feedback entries to return
 */
export async function getUserFeedback(limit = 10) {
    return apiRequest(`/feedback/?limit=${limit}`);
}

/**
 * Get feedback statistics (public - no auth required)
 */
export async function getFeedbackStats() {
    return publicApiRequest('/feedback/stats');
}

/**
 * Delete a feedback entry (requires auth, only own feedback)
 * @param {number} feedbackId - ID of the feedback to delete
 */
export async function deleteFeedback(feedbackId) {
    return apiRequest(`/feedback/${feedbackId}`, {
        method: 'DELETE',
    });
}
