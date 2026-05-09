CREATE TABLE IF NOT EXISTS trending_videos (
    video_id            VARCHAR PRIMARY KEY,
    title               TEXT,
    channel_id          VARCHAR,
    channel_title       VARCHAR,
    category_id         VARCHAR,
    category_name       VARCHAR,
    published_at        TIMESTAMP,
    extracted_at        TIMESTAMP,
    view_count          BIGINT,
    like_count          BIGINT,
    comment_count       BIGINT,
    duration_seconds    INTEGER,      -- converted from ISO 8601
    duration_minutes    FLOAT,        -- computed in transform
    tags                TEXT,         -- comma-separated
    thumbnail_url       TEXT,
    region_code         VARCHAR,
    title_length        INTEGER,      -- computed in transform
    title_word_count    INTEGER,      -- computed in transform
    has_numbers         BOOLEAN,      -- does title contain numbers?
    engagement_rate     FLOAT,        -- (likes+comments)/views * 100
    like_ratio          FLOAT,        -- likes / views * 100
    days_since_publish  INTEGER       -- age of video when it trended
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id           SERIAL PRIMARY KEY,
    run_at           TIMESTAMP DEFAULT NOW(),
    category         VARCHAR,
    videos_extracted INTEGER,
    videos_inserted  INTEGER,
    videos_skipped   INTEGER,
    status           VARCHAR,
    error_msg        TEXT
);

CREATE TABLE IF NOT EXISTS channel_stats (
    channel_id          VARCHAR PRIMARY KEY,
    extracted_at        TIMESTAMP,
    subscriber_count    BIGINT,
    total_video_count   INTEGER
);
;
