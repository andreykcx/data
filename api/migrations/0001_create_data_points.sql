-- Create storage for uploaded x,y pairs grouped by dataset.
CREATE TABLE IF NOT EXISTS data_points (
    id BIGSERIAL PRIMARY KEY,
    dataset_id UUID NOT NULL,
    x DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    y DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Optimize lookups by dataset.
CREATE INDEX IF NOT EXISTS idx_data_points_dataset_id ON data_points (dataset_id);
