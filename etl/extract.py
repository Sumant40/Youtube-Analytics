from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import logging
from config import YOUTUBE_API_KEY, CATEGORIES, REGION_CODE

logger = logging.getLogger(__name__)

def get_youtube_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def extract_trending_videos(category_id: str,
                            region: str = REGION_CODE,
                            max_results: int = 50) -> pd.DataFrame:
    """Extract trending videos for a given category."""
    youtube = get_youtube_client()

    request = youtube.videos().list(
        part        = "snippet,statistics,contentDetails",
        chart       = "mostPopular",
        regionCode  = region,
        videoCategoryId = category_id,
        maxResults  = max_results
    )
    response = request.execute()

    records = []
    for item in response.get("items", []):
        snippet  = item.get("snippet", {})
        stats    = item.get("statistics", {})
        content  = item.get("contentDetails", {})

        records.append({
            "video_id"      : item["id"],
            "title"         : snippet.get("title", ""),
            "channel_id"    : snippet.get("channelId", ""),
            "channel_title" : snippet.get("channelTitle", ""),
            "category_id"   : category_id,
            "category_name" : CATEGORIES.get(category_id, "Unknown"),
            "published_at"  : snippet.get("publishedAt", ""),
            "extracted_at"  : datetime.utcnow(),
            "view_count"    : stats.get("viewCount", 0),
            "like_count"    : stats.get("likeCount", 0),
            "comment_count" : stats.get("commentCount", 0),
            "duration"      : content.get("duration", "PT0S"),
            "tags"          : ",".join(snippet.get("tags", [])),
            "thumbnail_url" : snippet.get("thumbnails", {})
                                     .get("high", {})
                                     .get("url", ""),
            "region_code"   : region
        })

    logger.info(
        f"Extracted {len(records)} videos — "
        f"category {CATEGORIES.get(category_id)} / {region}"
    )
    return pd.DataFrame(records)

def extract_channel_stats(channel_ids: list) -> pd.DataFrame:
    """Extract subscriber counts for a list of channel IDs."""
    youtube = get_youtube_client()
    records = []

    # API allows max 50 channel IDs per request
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]
        resp  = youtube.channels().list(
            part = "statistics",
            id   = ",".join(batch)
        ).execute()

        for item in resp.get("items", []):
            stats = item.get("statistics", {})
            records.append({
                "channel_id"       : item["id"],
                "extracted_at"     : datetime.utcnow(),
                "subscriber_count" : int(stats.get("subscriberCount", 0)),
                "total_video_count": int(stats.get("videoCount", 0))
            })

    return pd.DataFrame(records)