-- Migration 008_auth_updates.sql
-- 1. Rename columns in users table
ALTER TABLE users RENAME COLUMN name TO full_name;
ALTER TABLE users RENAME COLUMN password_hash TO hashed_password;

-- 2. Create email_verifications table for OTP
CREATE TABLE email_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    otp_code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Index for fast lookup by user_id
CREATE INDEX idx_email_verifications_user_id ON email_verifications(user_id);
