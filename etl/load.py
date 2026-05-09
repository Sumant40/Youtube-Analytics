import pandas as pd
from sqlalchemy import create_engine, text
import logging
from config import DB_CONFIG

logger = logging.getLogger(__name__)

def get_engine():
    url = (f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
           f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    return create_engine(url)

def load_videos(df: pd.DataFrame) -> dict:
    """Insert videos, skip duplicates via ON CONFLICT DO NOTHING."""
    engine  = get_engine()
    inserted = 0
    skipped  = 0

    cols = [
        "video_id","title","channel_id","channel_title",
        "category_id","category_name","published_at","extracted_at",
        "view_count","like_count","comment_count",
        "duration_seconds","duration_minutes","tags","thumbnail_url",
        "region_code","title_length","title_word_count","has_numbers",
        "engagement_rate","like_ratio","days_since_publish"
    ]

    with engine.connect() as conn:
        for _, row in df[cols].iterrows():
            try:
                stmt = text(f"""
                    INSERT INTO trending_videos
                        ({", ".join(cols)})
                    VALUES
                        ({", ".join(":" + c for c in cols)})
                    ON CONFLICT (video_id) DO NOTHING
                """)
                result = conn.execute(stmt, row.to_dict())
                if result.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"Insert error {row['video_id']}: {e}")
        conn.commit()

    logger.info(f"Load: {inserted} inserted | {skipped} skipped")
    return {"inserted": inserted, "skipped": skipped}

def load_channel_stats(df: pd.DataFrame):
    engine = get_engine()
    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO channel_stats
                    (channel_id, extracted_at,
                     subscriber_count, total_video_count)
                VALUES (:channel_id, :extracted_at,
                        :subscriber_count, :total_video_count)
                ON CONFLICT (channel_id) DO UPDATE SET
                    extracted_at       = EXCLUDED.extracted_at,
                    subscriber_count   = EXCLUDED.subscriber_count,
                    total_video_count  = EXCLUDED.total_video_count
            """), row.to_dict())
        conn.commit()
    logger.info(f"Channel stats upserted: {len(df)} channels")

def log_pipeline_run(category, extracted,
                     inserted, skipped, status, error_msg=None):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO pipeline_runs
                (run_at, category, videos_extracted,
                 videos_inserted, videos_skipped, status, error_msg)
            VALUES (NOW(), :cat, :ex, :ins, :sk, :st, :err)
        """), {"cat": category, "ex": extracted,
               "ins": inserted,  "sk": skipped,
               "st": status,     "err": error_msg})
        conn.commit()
