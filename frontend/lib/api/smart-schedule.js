import { apiRequest } from './config';

/**
 * Smart Schedule API Service
 * 3-Layer Architecture Integration:
 * - Layer 1 (Brain): /api/extract - LangGraph + LLM
 * - Layer 2 (Solver): /api/schedule - OR-Tools CP-SAT
 * - Layer 3 (Memory): /api/feedback - Graphiti + Neo4j
 */

/**
 * Extract tasks from natural language (Layer 1: Brain)
 * @param {string} message - Natural language input
 * @returns {Promise<ExtractResponse>}
 */
export async function extractTasks(message) {
    return apiRequest('/api/extract', {
        method: 'POST',
        body: JSON.stringify({ message }),
    });
}

/**
 * Generate optimized schedule from tasks (Layer 2: Solver)
 * @param {Object} params - Schedule parameters
 * @param {Array} params.tasks - Extracted tasks
 * @param {Array} params.fixedSlots - Fixed time commitments
 * @param {string} params.dayStartTime - Day start in HH:MM
 * @param {string} params.dayEndTime - Day end in HH:MM
 * @param {string} params.scheduleDate - Date in YYYY-MM-DD
 * @param {Object} params.preferences - User preferences
 * @returns {Promise<ScheduleResponse>}
 */
export async function generateSchedule(params) {
    return apiRequest('/api/schedule', {
        method: 'POST',
        body: JSON.stringify({
            tasks: params.tasks,
            fixed_slots: params.fixedSlots || [],
            day_start_time: params.dayStartTime || '09:00',
            day_end_time: params.dayEndTime || '22:00',
            schedule_date: params.scheduleDate,
            preferences: params.preferences,
        }),
    });
}

/**
 * Submit feedback for pattern learning (Layer 3: Memory)
 * @param {Object} feedback - Feedback data
 * @param {'accepted'|'edited'|'rejected'} feedback.feedbackType
 * @param {string} feedback.taskName
 * @param {string} feedback.originalTime - For edits
 * @param {string} feedback.newTime - For edits
 * @param {string} feedback.reason - Optional reason
 * @returns {Promise<FeedbackResponse>}
 */
export async function submitFeedback(feedback) {
    return apiRequest('/api/feedback', {
        method: 'POST',
        body: JSON.stringify({
            feedback_type: feedback.feedbackType,
            task_name: feedback.taskName,
            original_time: feedback.originalTime,
            new_time: feedback.newTime,
            reason: feedback.reason,
        }),
    });
}

/**
 * Full pipeline: Extract + Schedule in one call
 * @param {string} description - Natural language description
 * @param {Object} options - Optional parameters
 * @returns {Promise<FullScheduleResponse>}
 */
export async function generateSmartSchedule(description, options = {}) {
    const { startHour = 9, endHour = 20, breakDuration = 15, fixedSlots = [] } = options;

    return apiRequest('/api/generate', {
        method: 'POST',
        body: JSON.stringify({
            description,
            day_start_time: `${String(Math.floor(startHour)).padStart(2, '0')}:00`,
            day_end_time: `${String(Math.floor(endHour)).padStart(2, '0')}:00`,
            fixed_slots: fixedSlots,
        }),
    });
}

/**
 * Set user defaults (wake/sleep time)
 * @param {string} wakeTime - Wake time in HH:MM
 * @param {string} sleepTime - Sleep time in HH:MM
 * @returns {Promise<FeedbackResponse>}
 */
export async function setUserDefaults(wakeTime, sleepTime) {
    return apiRequest('/api/user-defaults', {
        method: 'POST',
        body: JSON.stringify({
            wake_time: wakeTime,
            sleep_time: sleepTime,
        }),
    });
}

/**
 * Get status of all three layers
 * @returns {Promise<StatusResponse>}
 */
export async function getLayerStatus() {
    return apiRequest('/api/status');
}

/**
 * Transform backend scheduled block to frontend format
 * @param {Object} block - Backend schedule block
 * @returns {Object} Frontend formatted block
 */
export function transformScheduledBlock(block) {
    return {
        id: block.task_name.replace(/\s+/g, '-').toLowerCase(),
        name: block.task_name,
        startTime: block.start_time,
        endTime: block.end_time,
        reason: block.reason,
    };
}

/**
 * Transform backend scheduled task to frontend display format (legacy compat)
 * @param {Object} task - Backend scheduled task
 * @returns {Object} Frontend formatted task
 */
export function transformScheduledTask(task) {
    return {
        id: task.id || task.task_name?.replace(/\s+/g, '-').toLowerCase(),
        name: task.name || task.task_name,
        startTime: task.start_time,
        endTime: task.end_time,
        duration: task.duration,
        priority: task.priority,
        aiTip: task.tip || task.reason,
    };
}
