-- Store model outputs alongside their source inputs.
CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    dataset_id UUID NOT NULL,
    x DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    actual DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    predicted DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    residual DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Facilitate dataset-level retrieval of prediction rows.
CREATE INDEX IF NOT EXISTS idx_predictions_dataset_id ON predictions (dataset_id);
