import { apiRequest } from './config';

/**
 * Smart Schedule API Service
 * For natural language task input and AI-powered schedule generation
 */

/**
 * Parse a natural language description into tasks (preview only, no scheduling)
 * @param {string} description - Natural language description of tasks
 * @param {number} startHour - Start of scheduling window (default 9)
 * @param {number} endHour - End of scheduling window (default 20)
 * @returns {Promise<{success: boolean, message: string, tasks: Array}>}
 */
export async function parseTaskDescription(description, startHour = 9, endHour = 20) {
    return apiRequest('/smart-schedule/parse', {
        method: 'POST',
        body: JSON.stringify({
            description,
            start_hour: startHour,
            end_hour: endHour,
        }),
    });
}

/**
 * Generate an optimized schedule from natural language description
 * @param {string} description - Natural language description of tasks
 * @param {Object} options - Scheduling options
 * @param {number} options.startHour - Start of scheduling window (default 9)
 * @param {number} options.endHour - End of scheduling window (default 20)
 * @param {number} options.breakDuration - Break duration between tasks in minutes (default 15)
 * @returns {Promise<SmartScheduleResponse>}
 */
export async function generateSmartSchedule(description, options = {}) {
    const { startHour = 9, endHour = 20, breakDuration = 15 } = options;

    return apiRequest('/smart-schedule/generate', {
        method: 'POST',
        body: JSON.stringify({
            description,
            start_hour: startHour,
            end_hour: endHour,
            break_duration: breakDuration,
        }),
    });
}

/**
 * Generate schedule from pre-parsed task list
 * Use when you want to bypass natural language parsing
 * @param {Array<{name: string, duration: number, priority?: string}>} tasks - List of tasks
 * @param {Object} options - Scheduling options
 * @returns {Promise<SmartScheduleResponse>}
 */
export async function generateFromTasks(tasks, options = {}) {
    const { startHour = 9, endHour = 20, breakDuration = 15 } = options;

    const params = new URLSearchParams({
        start_hour: startHour.toString(),
        end_hour: endHour.toString(),
        break_duration: breakDuration.toString(),
    });

    return apiRequest(`/smart-schedule/generate-from-tasks?${params}`, {
        method: 'POST',
        body: JSON.stringify(tasks),
    });
}

/**
 * Transform backend scheduled task to frontend display format
 * @param {Object} task - Backend scheduled task
 * @returns {Object} Frontend formatted task
 */
export function transformScheduledTask(task) {
    return {
        id: task.id,
        name: task.name,
        startTime: task.start_time,
        endTime: task.end_time,
        duration: task.duration,
        priority: task.priority,
        aiTip: task.tip,
    };
}
