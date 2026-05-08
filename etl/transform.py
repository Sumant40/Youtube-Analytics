import pandas as pd
import isodate
from datetime import datetime, timezone
import logging
import re

logger = logging.getLogger(__name__)

def parse_duration(iso_duration: str) -> int:
    """Convert ISO 8601 duration (PT4M13S) to total seconds."""
    try:
        return int(isodate.parse_duration(iso_duration).total_seconds())
    except Exception:
        return 0

def transform_videos(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, validate, and enrich raw YouTube trending data."""
    original = len(df)

    # --- 1. Drop duplicates within batch ---
    df = df.drop_duplicates(subset="video_id")

    # --- 2. Fix data types ---
    for col in ["view_count","like_count","comment_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # --- 3. Parse timestamps ---
    df["published_at"] = pd.to_datetime(
        df["published_at"], utc=True, errors="coerce"
    ).dt.tz_localize(None)

    # --- 4. Parse duration ---
    df["duration_seconds"] = df["duration"].apply(parse_duration)
    df["duration_minutes"] = (df["duration_seconds"] / 60).round(2)

    # --- 5. Remove bad rows ---
    df = df[df["view_count"] > 0]
    df = df[df["duration_seconds"] > 0]
    df = df[df["title"].str.len() > 2]

    # --- 6. Feature engineering ---
    df["title_length"]      = df["title"].str.len()
    df["title_word_count"]  = df["title"].str.split().str.len()
    df["has_numbers"]       = df["title"].str.contains(r"\d", regex=True)

    df["engagement_rate"] = (
        (df["like_count"] + df["comment_count"]) /
        df["view_count"].replace(0, 1) * 100
    ).round(4)

    df["like_ratio"] = (
        df["like_count"] / df["view_count"].replace(0, 1) * 100
    ).round(4)

    now = datetime.utcnow()
    df["days_since_publish"] = (
        (now - df["published_at"].fillna(now))
        .dt.days.clip(lower=0)
    )

    # drop the raw duration column — we have duration_seconds now
    df = df.drop(columns=["duration"])

    removed = original - len(df)
    logger.info(f"Transform: {len(df)} clean rows | {removed} removed")
    return df
