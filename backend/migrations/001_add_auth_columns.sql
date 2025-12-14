-- ============================================================================
-- PULSE Database Migration: Add Authentication Columns
-- Version: 2.0.0
-- Date: 2025-12-15
-- 
-- This migration adds authentication support to the users table.
-- Run this in Supabase SQL Editor or via psql.
-- ============================================================================

-- Step 1: Add new columns to users table (if they don't exist)
-- Using IF NOT EXISTS pattern for idempotency

DO $$ 
BEGIN
    -- Add email column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'email') THEN
        ALTER TABLE users ADD COLUMN email VARCHAR(255);
        CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email);
    END IF;

    -- Add password_hash column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'password_hash') THEN
        ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
    END IF;

    -- Add is_active column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'is_active') THEN
        ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
    END IF;
END $$;

-- Step 2: Update existing users with placeholder values
-- This ensures existing users can still function

UPDATE users 
SET 
    email = COALESCE(email, 'user_' || id || '@pulse.local'),
    password_hash = COALESCE(password_hash, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.O/qH8vF/Y5QyHm'),  -- hashed 'pulse-default-2024'
    is_active = COALESCE(is_active, TRUE)
WHERE email IS NULL OR password_hash IS NULL;

-- Step 3: Make columns NOT NULL after populating data
-- Only run if you're sure all rows have values

-- ALTER TABLE users ALTER COLUMN email SET NOT NULL;
-- ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;

-- Step 4: Verify the migration
SELECT 
    id, 
    username, 
    email, 
    CASE WHEN password_hash IS NOT NULL THEN 'SET' ELSE 'NULL' END as password_status,
    is_active,
    created_at
FROM users;

-- ============================================================================
-- Notes:
-- - Default password for migrated users: 'pulse-default-2024'
-- - Email pattern for migrated users: 'user_{id}@pulse.local'
-- - Users should be prompted to change their password after migration
-- ============================================================================
