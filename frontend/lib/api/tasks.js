import { apiRequest } from './config';

/**
 * Tasks API Service
 */

export async function getTasks(completed = null) {
  const params = new URLSearchParams();
  if (completed !== null) {
    params.append('completed', completed);
  }
  const query = params.toString();
  return apiRequest(`/tasks${query ? `?${query}` : ''}`);
}

export async function getTask(taskId) {
  return apiRequest(`/tasks/${taskId}`);
}

export async function createTask(taskData) {
  // Map frontend format to backend format
  // Backend expects duration in hours, frontend uses minutes
  const durationMinutes = parseFloat(taskData.duration || taskData.estimatedTime || 60);
  const durationHours = durationMinutes / 60; // Convert minutes to hours
  
  const backendData = {
    title: taskData.name || taskData.title,
    description: taskData.description || null,
    duration: durationHours,
    difficulty: taskData.difficulty || 'medium',
    parent_id: taskData.parentId || null,
  };
  return apiRequest('/tasks', {
    method: 'POST',
    body: JSON.stringify(backendData),
  });
}

export async function updateTask(taskId, taskData) {
  // Map frontend format to backend format
  const backendData = {};
  if (taskData.name || taskData.title) {
    backendData.title = taskData.name || taskData.title;
  }
  if (taskData.duration || taskData.estimatedTime) {
    // Backend expects duration in hours, frontend uses minutes
    const durationMinutes = parseFloat(taskData.duration || taskData.estimatedTime);
    backendData.duration = durationMinutes / 60; // Convert minutes to hours
  }
  if (taskData.difficulty) {
    backendData.difficulty = taskData.difficulty;
  }
  if (taskData.done !== undefined) {
    backendData.completed = taskData.done;
  }
  
  return apiRequest(`/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify(backendData),
  });
}

export async function deleteTask(taskId) {
  return apiRequest(`/tasks/${taskId}`, {
    method: 'DELETE',
  });
}

export async function toggleTask(taskId) {
  return apiRequest(`/tasks/${taskId}/toggle`, {
    method: 'POST',
  });
}

export async function scheduleTask(taskId, startTime) {
  return apiRequest(`/tasks/${taskId}/schedule?start_time=${startTime}`, {
    method: 'POST',
  });
}

/**
 * Transform backend task to frontend format
 */
export function transformTask(backendTask) {
  // Backend stores duration in hours, convert to minutes for frontend
  const durationMinutes = Math.round((backendTask.duration || 0) * 60);
  const hours = Math.floor(durationMinutes / 60);
  const minutes = durationMinutes % 60;
  const timeStr = hours > 0
    ? `${hours}h${minutes > 0 ? ` ${minutes} min` : ''}`.trim()
    : `${minutes} min`;

  return {
    id: backendTask.id,
    name: backendTask.title, // Primary display name
    task: backendTask.title, // Alias for compatibility
    title: backendTask.title, // Alias for compatibility
    done: backendTask.completed,
    completed: backendTask.completed,
    time: timeStr,
    duration: durationMinutes, // Store in minutes for frontend
    difficulty: backendTask.difficulty,
    scheduled_at: backendTask.scheduledAt || backendTask.scheduled_at,
    description: backendTask.description,
    parentId: backendTask.parentId || backendTask.parent_id,
    subtasks: [], // Will be populated separately
  };
}

