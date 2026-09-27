-- Agent Supply Chain Security — Database Schema
-- PostgreSQL 16 with pgvector extension

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- SBOM records
CREATE TABLE IF NOT EXISTS sbom_records (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artifact_name    VARCHAR(255) NOT NULL,
    artifact_version VARCHAR(255) NOT NULL,
    image_digest     VARCHAR(71),
    sbom_digest      VARCHAR(64) NOT NULL,
    storage_uri      TEXT NOT NULL,
    attestation      JSONB NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tenant_id        VARCHAR(255) NOT NULL DEFAULT 'default'
);

CREATE INDEX idx_sbom_artifact ON sbom_records(artifact_name, artifact_version);
CREATE INDEX idx_sbom_digest ON sbom_records(image_digest) WHERE image_digest IS NOT NULL;
CREATE INDEX idx_sbom_tenant ON sbom_records(tenant_id);

-- Provenance records
CREATE TABLE IF NOT EXISTS provenance_records (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    image_digest    VARCHAR(71) NOT NULL UNIQUE,
    status          VARCHAR(50) NOT NULL,
    slsa_level      INTEGER NOT NULL DEFAULT 0,
    violations      JSONB NOT NULL DEFAULT '[]',
    warnings        JSONB NOT NULL DEFAULT '[]',
    provenance_data JSONB,
    retrieved_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_provenance_digest ON provenance_records(image_digest);

-- Vulnerability scan records
CREATE TABLE IF NOT EXISTS vulnerability_scans (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id         VARCHAR(255) NOT NULL UNIQUE,
    total_packages  INTEGER NOT NULL,
    findings        JSONB NOT NULL DEFAULT '[]',
    policy_decision VARCHAR(10) NOT NULL,
    policy_reason   TEXT NOT NULL,
    critical_count  INTEGER NOT NULL DEFAULT 0,
    high_count      INTEGER NOT NULL DEFAULT 0,
    scanned_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tenant_id       VARCHAR(255) NOT NULL DEFAULT 'default'
);

CREATE INDEX idx_vuln_scan_tenant ON vulnerability_scans(tenant_id);
CREATE INDEX idx_vuln_scan_policy ON vulnerability_scans(policy_decision);

-- RAG document chunks with vector embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_id      VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(1024),
    metadata    JSONB NOT NULL DEFAULT '{}',
    source_url  TEXT,
    acl_tags    TEXT[] DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chunks_doc ON document_chunks(doc_id);
CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Session ledger for agent runs
CREATE TABLE IF NOT EXISTS agent_sessions (
    session_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type      VARCHAR(100) NOT NULL,
    tenant_id       VARCHAR(255) NOT NULL DEFAULT 'default',
    input_hash      VARCHAR(64) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'running',
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    output          JSONB,
    error           TEXT,
    idempotency_key VARCHAR(255) UNIQUE
);

CREATE INDEX idx_sessions_tenant ON agent_sessions(tenant_id);
CREATE INDEX idx_sessions_idempotency ON agent_sessions(idempotency_key)
    WHERE idempotency_key IS NOT NULL;
