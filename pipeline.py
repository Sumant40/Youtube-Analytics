import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl.extract   import extract_trending_videos, extract_channel_stats
from etl.transform import transform_videos
from etl.load      import load_videos, load_channel_stats, log_pipeline_run
from config        import CATEGORIES, DB_CONFIG
import logging
import pandas as pd
from sqlalchemy import create_engine

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level    = logging.INFO,
    format   = "%(asctime)s | %(levelname)s | %(message)s",
    handlers = [
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)

# ── Step 1: ETL for each category ─────────────────────────────
for cat_id, cat_name in CATEGORIES.items():
    try:
        raw_df   = extract_trending_videos(cat_id)
        clean_df = transform_videos(raw_df)
        counts   = load_videos(clean_df)
        log_pipeline_run(cat_name, len(raw_df),
                         counts["inserted"], counts["skipped"], "success")
    except Exception as e:
        logging.error(f"FAILED for {cat_name}: {e}")
        log_pipeline_run(cat_name, 0, 0, 0, "failed", str(e))

# ── Step 2: Channel stats ──────────────────────────────────────
try:
    engine = create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    channel_ids = pd.read_sql(
        "SELECT DISTINCT channel_id FROM trending_videos", engine
    )["channel_id"].tolist()

    ch_df = extract_channel_stats(channel_ids)
    load_channel_stats(ch_df)
    logging.info(f"Channel stats loaded: {len(ch_df)} channels")
except Exception as e:
    logging.error(f"Channel stats failed: {e}")

print("Pipeline run complete.")