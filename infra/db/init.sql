-- Norsk: Kjerne for PrioritiAI
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS prioai_task (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    source VARCHAR(32) NOT NULL,
    source_ref TEXT,
    requester TEXT,
    role_hint TEXT,
    due_at TIMESTAMPTZ,
    est_minutes INT,
    value_score INT DEFAULT 0,
    risk_score INT DEFAULT 0,
    role_score INT DEFAULT 0,
    haste_score INT DEFAULT 0,
    ai_score INT DEFAULT 0,
    ai_reason TEXT,
    status VARCHAR(24) NOT NULL DEFAULT 'incoming',
    override_priority INT,
    override_locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_status ON prioai_task(status);
CREATE INDEX IF NOT EXISTS idx_task_due ON prioai_task(due_at);
