/**
 * Tasks API Module
 * CRUD operations for task management
 */

import { apiClient } from './client';

// ============ Types ============

/** Backend task response format */
export interface BackendTask {
    id: number;
    title: string;
    duration: number;
    durationMinutes: number;
    completed: boolean;
    priority: 'low' | 'medium' | 'high';
    difficulty: 'easy' | 'medium' | 'hard';
    scheduledAt: string | null;
    createdAt: string;
    updatedAt: string | null;
}

/** Frontend task format */
export interface Task {
    id: number;
    name: string;
    duration: number; // in minutes
    done: boolean;
    priority: 'low' | 'medium' | 'high';
    difficulty: 'easy' | 'medium' | 'hard';
    scheduledAt: string | null;
    createdAt: string;
    updatedAt: string | null;
}

/** Create task payload */
export interface TaskCreate {
    title: string;
    durationMinutes?: number;
    duration?: number;
    difficulty?: 'easy' | 'medium' | 'hard';
    priority?: 'low' | 'medium' | 'high';
}

/** Update task payload */
export interface TaskUpdate {
    title?: string;
    durationMinutes?: number;
    duration?: number;
    difficulty?: 'easy' | 'medium' | 'hard';
    priority?: 'low' | 'medium' | 'high';
    completed?: boolean;
}

// ============ Transformation ============

/**
 * Transform backend task to frontend format
 */
export function transformTask(backend: BackendTask): Task {
    return {
        id: backend.id,
        name: backend.title,
        duration: backend.durationMinutes,
        done: backend.completed,
        priority: backend.priority,
        difficulty: backend.difficulty,
        scheduledAt: backend.scheduledAt,
        createdAt: backend.createdAt,
        updatedAt: backend.updatedAt,
    };
}

// ============ API Methods ============

export const tasksApi = {
    /**
     * Get all tasks
     */
    async getAll(params?: { completed?: boolean }): Promise<Task[]> {
        let endpoint = '/tasks';
        if (params?.completed !== undefined) {
            endpoint += `?completed=${params.completed}`;
        }
        const tasks = await apiClient<BackendTask[]>(endpoint);
        return tasks.map(transformTask);
    },

    /**
     * Get single task by ID
     */
    async getById(id: number): Promise<Task> {
        const task = await apiClient<BackendTask>(`/tasks/${id}`);
        return transformTask(task);
    },

    /**
     * Create new task
     */
    async create(data: TaskCreate): Promise<Task> {
        const task = await apiClient<BackendTask>('/tasks', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        return transformTask(task);
    },

    /**
     * Update existing task
     */
    async update(id: number, data: TaskUpdate): Promise<Task> {
        const task = await apiClient<BackendTask>(`/tasks/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
        return transformTask(task);
    },

    /**
     * Delete task
     */
    async delete(id: number): Promise<void> {
        await apiClient<void>(`/tasks/${id}`, {
            method: 'DELETE',
        });
    },

    /**
     * Toggle task completion status
     */
    async toggle(id: number): Promise<Task> {
        const task = await apiClient<BackendTask>(`/tasks/${id}/toggle`, {
            method: 'POST',
        });
        return transformTask(task);
    },
};

export default tasksApi;
