/**
 * API Module Index
 * Re-exports all API modules for convenient importing
 */

// Configuration
export { API_CONFIG } from './config';
export type { ApiConfig } from './config';

// Base client
export { apiClient, ApiError } from './client';

// Tasks API
export { tasksApi, transformTask } from './tasks';
export type {
    Task,
    BackendTask,
    TaskCreate,
    TaskUpdate
} from './tasks';

// Schedule API
export { scheduleApi, transformScheduleBlock } from './schedule';
export type {
    ScheduleBlock,
    BackendScheduleBlock,
    ScheduleBlockCreate,
    ScheduleBlockUpdate,
    BlockType
} from './schedule';

// Mood API
export { moodApi } from './mood';
export type {
    MoodEntry,
    MoodValue,
    MoodCreate,
    MoodCounts,
    MostCommonMood,
    CurrentMood
} from './mood';

// Reflections API
export { reflectionsApi } from './reflections';
export type {
    Reflection,
    ReflectionCreate,
    ReflectionUpdate,
    MoodAverage,
    CommonDistraction,
    CommonDistractionsResponse
} from './reflections';
