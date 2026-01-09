-- ============================================
-- UoV AI Assistant - Supabase Database Schema
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Table: chat_sessions
-- Purpose: Store chat session metadata
-- ============================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at 
ON chat_sessions(created_at DESC);

-- ============================================
-- Table: chat_messages
-- Purpose: Store all chat messages (user + assistant)
-- ============================================
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    citations JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id 
ON chat_messages(session_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at 
ON chat_messages(created_at DESC);

-- ============================================
-- Table: feedback
-- Purpose: Store user feedback on assistant responses
-- ============================================
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    message_id UUID NOT NULL REFERENCES chat_messages(message_id) ON DELETE CASCADE,
    rating VARCHAR(10) NOT NULL CHECK (rating IN ('up', 'down')),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics
CREATE INDEX IF NOT EXISTS idx_feedback_session_id 
ON feedback(session_id);

CREATE INDEX IF NOT EXISTS idx_feedback_message_id 
ON feedback(message_id);

CREATE INDEX IF NOT EXISTS idx_feedback_rating 
ON feedback(rating);

CREATE INDEX IF NOT EXISTS idx_feedback_created_at 
ON feedback(created_at DESC);

-- ============================================
-- Table: request_logs
-- Purpose: Store API request metadata for monitoring
-- ============================================
CREATE TABLE IF NOT EXISTS request_logs (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(session_id) ON DELETE SET NULL,
    endpoint VARCHAR(100),
    latency_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for monitoring queries
CREATE INDEX IF NOT EXISTS idx_request_logs_session_id 
ON request_logs(session_id);

CREATE INDEX IF NOT EXISTS idx_request_logs_endpoint 
ON request_logs(endpoint);

CREATE INDEX IF NOT EXISTS idx_request_logs_created_at 
ON request_logs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_request_logs_error 
ON request_logs(error) WHERE error IS NOT NULL;

-- ============================================
-- Table: documents (optional metadata)
-- Purpose: Store document metadata for ingested files
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    source_file VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    total_chunks INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for document lookups
CREATE INDEX IF NOT EXISTS idx_documents_source_file 
ON documents(source_file);

CREATE INDEX IF NOT EXISTS idx_documents_created_at 
ON documents(created_at DESC);

-- ============================================
-- Views for Analytics
-- ============================================

-- View: Session statistics
CREATE OR REPLACE VIEW session_stats AS
SELECT 
    cs.session_id,
    cs.created_at,
    COUNT(cm.message_id) as message_count,
    COUNT(CASE WHEN cm.role = 'user' THEN 1 END) as user_messages,
    COUNT(CASE WHEN cm.role = 'assistant' THEN 1 END) as assistant_messages,
    COUNT(f.feedback_id) as feedback_count,
    COUNT(CASE WHEN f.rating = 'up' THEN 1 END) as positive_feedback,
    COUNT(CASE WHEN f.rating = 'down' THEN 1 END) as negative_feedback
FROM chat_sessions cs
LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
LEFT JOIN feedback f ON cs.session_id = f.session_id
GROUP BY cs.session_id, cs.created_at;

-- View: Daily metrics
CREATE OR REPLACE VIEW daily_metrics AS
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(*) as total_messages
FROM chat_messages
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================
-- Comments for documentation
-- ============================================
COMMENT ON TABLE chat_sessions IS 'Stores chat session metadata';
COMMENT ON TABLE chat_messages IS 'Stores all chat messages with citations';
COMMENT ON TABLE feedback IS 'Stores user feedback on assistant responses';
COMMENT ON TABLE request_logs IS 'Stores API request logs for monitoring';
COMMENT ON TABLE documents IS 'Stores metadata for ingested documents';
