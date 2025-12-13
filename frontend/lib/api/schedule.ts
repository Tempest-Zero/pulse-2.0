/**
 * Schedule API Module
 * CRUD operations for schedule block management
 */

import { apiClient } from './client';

// ============ Types ============

/** Schedule block types */
export type BlockType = 'fixed' | 'focus' | 'break' | 'task';

/** Backend schedule block format */
export interface BackendScheduleBlock {
    id: number;
    title: string;
    start: number;
    duration: number;
    type: BlockType;
    createdAt: string;
    updatedAt: string | null;
}

/** Frontend schedule block format */
export interface ScheduleBlock {
    id: number;
    title: string;
    start: number;
    duration: number;
    blockType: BlockType;
    createdAt: string;
    updatedAt: string | null;
}

/** Create schedule block payload */
export interface ScheduleBlockCreate {
    title: string;
    start: number;
    duration: number;
    block_type?: BlockType;
}

/** Update schedule block payload */
export interface ScheduleBlockUpdate {
    title?: string;
    start?: number;
    duration?: number;
    block_type?: BlockType;
}

// ============ Transformation ============

/**
 * Transform backend schedule block to frontend format
 */
export function transformScheduleBlock(backend: BackendScheduleBlock): ScheduleBlock {
    return {
        id: backend.id,
        title: backend.title,
        start: backend.start,
        duration: backend.duration,
        blockType: backend.type,
        createdAt: backend.createdAt,
        updatedAt: backend.updatedAt,
    };
}

// ============ API Methods ============

export const scheduleApi = {
    /**
     * Get all schedule blocks
     */
    async getAll(params?: { type?: BlockType }): Promise<ScheduleBlock[]> {
        let endpoint = '/schedule';
        if (params?.type) {
            endpoint += `?block_type=${params.type}`;
        }
        const blocks = await apiClient<BackendScheduleBlock[]>(endpoint);
        return blocks.map(transformScheduleBlock);
    },

    /**
     * Get single schedule block by ID
     */
    async getById(id: number): Promise<ScheduleBlock> {
        const block = await apiClient<BackendScheduleBlock>(`/schedule/${id}`);
        return transformScheduleBlock(block);
    },

    /**
     * Create new schedule block
     */
    async create(data: ScheduleBlockCreate): Promise<ScheduleBlock> {
        const block = await apiClient<BackendScheduleBlock>('/schedule', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        return transformScheduleBlock(block);
    },

    /**
     * Update existing schedule block
     */
    async update(id: number, data: ScheduleBlockUpdate): Promise<ScheduleBlock> {
        const block = await apiClient<BackendScheduleBlock>(`/schedule/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
        return transformScheduleBlock(block);
    },

    /**
     * Delete schedule block
     */
    async delete(id: number): Promise<void> {
        await apiClient<void>(`/schedule/${id}`, {
            method: 'DELETE',
        });
    },

    /**
     * Get blocks in time range
     */
    async getInRange(startHour: number, endHour: number): Promise<ScheduleBlock[]> {
        const blocks = await apiClient<BackendScheduleBlock[]>(
            `/schedule/range?start_hour=${startHour}&end_hour=${endHour}`
        );
        return blocks.map(transformScheduleBlock);
    },

    /**
     * Clear all schedule blocks
     */
    async clearAll(): Promise<void> {
        await apiClient<void>('/schedule', {
            method: 'DELETE',
        });
    },
};

export default scheduleApi;
