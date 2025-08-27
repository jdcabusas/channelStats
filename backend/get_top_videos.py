import sys
import os
import requests
import re
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==============================
#  CONFIG
# ==============================
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# YouTube API endpoints
CHANNELS_API_URL = "https://www.googleapis.com/youtube/v3/channels"
PLAYLIST_ITEMS_API_URL = "https://www.googleapis.com/youtube/v3/playlistItems"
VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"


# ==============================
#  HELPER FUNCTIONS
# ==============================
def extract_channel_id_from_url(channel_url: str, api_key: str) -> str:
    """
    Takes a YouTube channel URL and returns the channel ID.
    Handles two main cases:
      1) Handle-based URL: "https://www.youtube.com/@SomeHandle"
         -> uses channels.list(forHandle='SomeHandle') to get channel ID
      2) Standard channel URL: "https://www.youtube.com/channel/UC-lHJZR3Gqxm24_Vd_AJ5Yw"
         -> parses out the channel ID directly
    """
    channel_url = channel_url.strip()

    # Case 1: handle-based URL
    if "/@" in channel_url:
        handle_part = channel_url.split("/@")[-1]
        handle_part = handle_part.split("?")[0]  # remove query params
        handle_no_at = handle_part.lstrip('@')   # remove leading '@' if any

        # Look up channel ID using forHandle
        params = {
            "part": "id",
            "forHandle": handle_no_at,
            "key": api_key
        }
        resp = requests.get(CHANNELS_API_URL, params=params).json()
        items = resp.get("items", [])
        if not items:
            raise ValueError(f"No channel found for handle: @{handle_no_at}. API response: {resp}")
        channel_id = items[0]["id"]
        return channel_id

    # Case 2: /channel/UC...
    if "/channel/" in channel_url:
        cid = channel_url.split("/channel/")[-1]
        cid = cid.split("?")[0]  # remove query params if any
        return cid

    raise ValueError(
        f"Could not determine channel ID from URL '{channel_url}'. "
        "If the URL is a custom /c/ or other format, please adapt the function."
    )


def parse_duration(duration_str: str) -> int:
    """
    Parse an ISO 8601 YouTube duration string (e.g. 'PT1H2M30S', 'PT13M', 'PT52S')
    and return the total length in seconds.
    """
    pattern = r"^PT(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+)S)?$"
    match = re.match(pattern, duration_str)
    if not match:
        return 0
    hours = int(match.group("h")) if match.group("h") else 0
    minutes = int(match.group("m")) if match.group("m") else 0
    seconds = int(match.group("s")) if match.group("s") else 0
    return hours * 3600 + minutes * 60 + seconds


def get_uploads_playlist_id(channel_id: str, api_key: str) -> str:
    """
    Given a channel ID, retrieve the channel's "uploads" playlist ID
    (which includes all public videos).
    """
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": api_key
    }
    resp = requests.get(CHANNELS_API_URL, params=params).json()
    items = resp.get("items", [])
    if not items:
        raise ValueError(f"No channel found for ID={channel_id}. Response: {resp}")

    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_all_videos_in_playlist(playlist_id: str, api_key: str) -> list:
    """
    Retrieve *all* video IDs from the given playlist, iterating through pages.
    Returns a list of video IDs.
    """
    video_ids = []
    page_token = None

    while True:
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": api_key
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(PLAYLIST_ITEMS_API_URL, params=params).json()
        items_this_page = resp.get("items", [])

        for item in items_this_page:
            snippet = item.get("snippet", {})
            resource_id = snippet.get("resourceId", {})
            if resource_id.get("kind") == "youtube#video":
                video_ids.append(resource_id.get("videoId"))

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return video_ids


def chunk_list(lst, chunk_size=50):
    """Yield successive chunks of size chunk_size from the list."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def get_videos_details(video_ids: list, api_key: str) -> dict:
    """
    Given a list of video IDs, fetch snippet, statistics, and contentDetails
    for each video in chunks of up to 50 IDs (YouTube API limit).
    Returns a dict: {video_id: {...}, ...}.
    """
    results = {}

    for chunk in chunk_list(video_ids, 50):
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(chunk),
            "maxResults": 50,
            "key": api_key
        }
        resp = requests.get(VIDEOS_API_URL, params=params).json()

        for item in resp.get("items", []):
            vid_id = item["id"]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content_details = item.get("contentDetails", {})

            duration_seconds = parse_duration(content_details.get("duration", "PT0S"))
            is_short = (duration_seconds < 60)

            results[vid_id] = {
                "title": snippet.get("title"),
                "publishedAt": snippet.get("publishedAt"),
                "viewCount": int(stats.get("viewCount", 0)),
                "likeCount": int(stats.get("likeCount", 0)) if "likeCount" in stats else 0,
                "commentCount": int(stats.get("commentCount", 0)) if "commentCount" in stats else 0,
                "durationSec": duration_seconds,
                "isShort": is_short
            }

    return results


def get_channel_videos_and_shorts(channel_url: str, api_key: str) -> (pd.DataFrame, pd.DataFrame):
    """
    Takes a YouTube channel URL (handle or '/channel/UC...'),
    uses the given YouTube Data API key to fetch:
      1) All public videos from the channel's "uploads" playlist
      2) Their details (title, stats, duration)
[I      3) Splits them into two DataFrames: (df_videos, df_shorts)
         both sorted by descending viewCount.
    Returns: (df_videos, df_shorts)
    """
    # 1) Extract channel ID
    channel_id = extract_channel_id_from_url(channel_url, api_key)

    # 2) Get uploads playlist
    uploads_playlist_id = get_uploads_playlist_id(channel_id, api_key)

    # 3) Fetch all video IDs
    all_video_ids = get_all_videos_in_playlist(uploads_playlist_id, api_key)
    if not all_video_ids:
        print("No videos found. Returning empty DataFrames.")
        return pd.DataFrame(), pd.DataFrame()

    # 4) Get full details
    videos_details = get_videos_details(all_video_ids, api_key)

    # 5) Build DataFrame
    rows = []
    for vid_id, info in videos_details.items():
        video_url = f"https://www.youtube.com/watch?v={vid_id}"
        row_data = {
            "videoId": vid_id,
            "url": video_url,
            "title": info["title"],
            "publishedAt": info["publishedAt"],
            "viewCount": info["viewCount"],
            "likeCount": info["likeCount"],
            "commentCount": info["commentCount"],
            "durationSec": info["durationSec"],
            "isShort": info["isShort"]
        }
        rows.append(row_data)

    df_all = pd.DataFrame(rows)

    # 6) Separate normal videos vs. shorts
    df_videos = df_all[df_all["isShort"] == False].copy()
    df_shorts = df_all[df_all["isShort"] == True].copy()

    # Sort each by descending viewCount
    df_videos.sort_values(by="viewCount", ascending=False, inplace=True)
    df_shorts.sort_values(by="viewCount", ascending=False, inplace=True)

    df_videos.reset_index(drop=True, inplace=True)
    df_shorts.reset_index(drop=True, inplace=True)

    return df_videos, df_shorts


# ==============================
#    COMMAND-LINE INTERFACE
# ==============================
def main():
    """
    Entry point when running from command line.
    Usage:
      python script.py <channel_url>
    Example:
      python script.py "https://www.youtube.com/@SomeChannel"
    """
    if len(sys.argv) < 2:
        print("Usage: python script.py <channel_url>")
        sys.exit(1)

    channel_url = sys.argv[1]
    print(f"Fetching videos for channel URL: {channel_url}")

    df_videos, df_shorts = get_channel_videos_and_shorts(channel_url, YOUTUBE_API_KEY)

    # Print some summary info
    print(f"\nTotal Videos: {len(df_videos)}, Shorts: {len(df_shorts)}")

    print("\n=== Top 5 Videos by viewCount ===")
    print(df_videos.head(5))

    print("\n=== Top 5 Shorts by viewCount ===")
    print(df_shorts.head(5))


if __name__ == "__main__":
    main()

