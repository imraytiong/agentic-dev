-- DBA Mandate: Enable pgvector and define base schema
CREATE EXTENSION IF NOT EXISTS vector;

-- Create state_records table for IStateStore/IVectorStore
CREATE TABLE IF NOT EXISTS state_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    data JSONB NOT NULL DEFAULT '{}',
    embedding vector(1536), -- Default for many OpenAI/Gemini models, can be adjusted
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create an HNSW index for the embedding column for efficient similarity search
CREATE INDEX IF NOT EXISTS state_records_embedding_idx ON state_records USING hnsw (embedding vector_cosine_ops);

-- Index for JSONB data lookups
CREATE INDEX IF NOT EXISTS state_records_data_idx ON state_records USING gin (data);
