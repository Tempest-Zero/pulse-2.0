import { apiRequest } from './config';

/**
 * Schedule API Service
 */

export async function getScheduleBlocks(blockType = null) {
  const params = new URLSearchParams();
  if (blockType) {
    params.append('block_type', blockType);
  }
  const query = params.toString();
  return apiRequest(`/schedule${query ? `?${query}` : ''}`);
}

export async function getScheduleBlocksInRange(startHour, endHour) {
  return apiRequest(`/schedule/range?start_hour=${startHour}&end_hour=${endHour}`);
}

export async function getScheduleBlock(blockId) {
  return apiRequest(`/schedule/${blockId}`);
}

export async function createScheduleBlock(blockData) {
  // Map frontend format to backend format
  // Backend expects duration in hours, frontend might use minutes
  let duration = parseFloat(blockData.duration);
  // If duration seems like minutes (> 8), convert to hours
  if (duration > 8) {
    duration = duration / 60;
  }
  
  const backendData = {
    title: blockData.title || blockData.name,
    start: parseFloat(blockData.start),
    duration: duration,
    block_type: blockData.block_type || blockData.type || 'task',
  };
  return apiRequest('/schedule', {
    method: 'POST',
    body: JSON.stringify(backendData),
  });
}

export async function updateScheduleBlock(blockId, blockData) {
  const backendData = {};
  if (blockData.title || blockData.name) {
    backendData.title = blockData.title || blockData.name;
  }
  if (blockData.start !== undefined) {
    backendData.start = parseFloat(blockData.start);
  }
  if (blockData.duration !== undefined) {
    backendData.duration = parseFloat(blockData.duration);
  }
  if (blockData.block_type || blockData.type) {
    backendData.block_type = blockData.block_type || blockData.type;
  }
  
  return apiRequest(`/schedule/${blockId}`, {
    method: 'PATCH',
    body: JSON.stringify(backendData),
  });
}

export async function deleteScheduleBlock(blockId) {
  return apiRequest(`/schedule/${blockId}`, {
    method: 'DELETE',
  });
}

export async function clearAllScheduleBlocks() {
  return apiRequest('/schedule', {
    method: 'DELETE',
  });
}

/**
 * Upload class schedule image
 */
export async function uploadClassSchedule(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const response = await fetch(`${API_BASE_URL}/schedule/upload-class-schedule`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }
  
  return response.json();
}

/**
 * Get available time slots that don't conflict with fixed schedule
 */
export async function getAvailableSlots(startHour = 9.0, endHour = 20.0, duration = 1.0) {
  return apiRequest(`/schedule/available-slots?start_hour=${startHour}&end_hour=${endHour}&duration=${duration}`);
}

/**
 * Transform backend schedule block to frontend format
 */
export function transformScheduleBlock(backendBlock) {
  // Backend stores start and duration in hours (0-24)
  const startHour = Math.floor(backendBlock.start);
  const startMin = Math.floor((backendBlock.start % 1) * 60);
  const endTimeHours = backendBlock.start + backendBlock.duration;
  const endHour = Math.floor(endTimeHours);
  const endMin = Math.floor((endTimeHours % 1) * 60);

  const startTime = new Date();
  startTime.setHours(startHour, startMin, 0, 0);

  const endTime = new Date();
  endTime.setHours(endHour, endMin, 0, 0);

  // Convert duration from hours to minutes for frontend
  const durationMinutes = Math.round(backendBlock.duration * 60);

  return {
    id: backendBlock.id,
    taskId: backendBlock.taskId || backendBlock.task_id, // Link to task
    name: backendBlock.title,
    title: backendBlock.title,
    duration: durationMinutes, // Store in minutes for frontend
    startTime: startTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
    endTime: endTime.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
    type: backendBlock.type || backendBlock.block_type,
  };
}

