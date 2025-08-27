import sys
import os
import pandas as pd
from get_top_videos import get_channel_videos_and_shorts
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==============================
#    CONFIGURATION
# ==============================
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# ==============================
#    COMMAND-LINE INTERFACE
# ==============================
def get_videos(channel_url, start_date_str=None, end_date_str=None, keyword=None):
    """
    Entry point for fetching videos with optional date filtering and keyword search.
    
    Args:
        channel_url (str): YouTube channel URL
        start_date_str (str, optional): Start date in YYYY-MM-DD format
        end_date_str (str, optional): End date in YYYY-MM-DD format
        keyword (str, optional): Keyword to search in title and description
    
    Returns:
        tuple: (df_videos_sorted, df_shorts_sorted) - Filtered and sorted DataFrames
    """
    print(f"Fetching videos for channel URL: {channel_url}\n")

    # Parse and validate the dates if provided
    start_date = None
    end_date = None
    
    if start_date_str and end_date_str:
        try:
            start_date = pd.to_datetime(start_date_str, format="%Y-%m-%d", utc=True)
        except ValueError:
            raise ValueError("Start date is not in the correct format (YYYY-MM-DD).")

        try:
            end_date = pd.to_datetime(end_date_str, format="%Y-%m-%d", utc=True) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        except ValueError:
            raise ValueError("End date is not in the correct format (YYYY-MM-DD).")

        if end_date < start_date:
            raise ValueError("End date cannot be earlier than start date.")

    # Fetch videos and shorts DataFrames
    df_videos, df_shorts = get_channel_videos_and_shorts(channel_url, YOUTUBE_API_KEY)

    # Log total videos retrieved
    print(f"Total Videos Retrieved: {len(df_videos)}, Shorts Retrieved: {len(df_shorts)}\n")

    # Apply date filtering if dates are provided
    if start_date and end_date:
        df_videos_filtered = filter_videos_by_date(df_videos, start_date, end_date)
        df_shorts_filtered = filter_videos_by_date(df_shorts, start_date, end_date)
        print(f"Videos within date range: {len(df_videos_filtered)}, Shorts within date range: {len(df_shorts_filtered)}\n")
    else:
        df_videos_filtered = df_videos.copy()
        df_shorts_filtered = df_shorts.copy()
        print("Using all videos (no date filtering)\n")

    # Apply keyword filtering if keyword is provided
    if keyword:
        df_videos_filtered = filter_videos_by_keyword(df_videos_filtered, keyword)
        df_shorts_filtered = filter_videos_by_keyword(df_shorts_filtered, keyword)
        print(f"Videos matching keyword '{keyword}': {len(df_videos_filtered)}, Shorts matching keyword: {len(df_shorts_filtered)}\n")

    # Sort filtered DataFrames by viewCount descending
    df_videos_sorted = df_videos_filtered.sort_values(by="viewCount", ascending=False).reset_index(drop=True)
    df_shorts_sorted = df_shorts_filtered.sort_values(by="viewCount", ascending=False).reset_index(drop=True)

    # Display results based on filtering applied
    if start_date and end_date:
        date_info = f"from {start_date.date()} to {end_date.date()}"
    else:
        date_info = "(all time)"
    
    keyword_info = f" matching '{keyword}'" if keyword else ""
    
    print(f"=== Top 15 Videos by View Count {date_info}{keyword_info} ===")
    if not df_videos_sorted.empty:
        print(df_videos_sorted.head(15)[['title', 'viewCount', 'url', 'publishedAt']].to_string(index=False))
    else:
        print("No normal videos found matching the criteria.")

    print(f"\n=== Top 15 Shorts by View Count {date_info}{keyword_info} ===")
    if not df_shorts_sorted.empty:
        print(df_shorts_sorted.head(15)[['title', 'viewCount', 'url', 'publishedAt']].to_string(index=False))
    else:
        print("No shorts found matching the criteria.")

    return df_videos_sorted, df_shorts_sorted

def filter_videos_by_date(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """
    Filters the DataFrame to include only videos published between start_date and end_date.

    Args:
        df (pd.DataFrame): DataFrame containing videos or shorts.
        start_date (pd.Timestamp): Start date (timezone-aware).
        end_date (pd.Timestamp): End date (timezone-aware).

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    # Ensure 'publishedAt' is datetime and timezone-aware
    if not pd.api.types.is_datetime64_any_dtype(df['publishedAt']):
        df['publishedAt'] = pd.to_datetime(df['publishedAt'], utc=True, errors='coerce')

    # Drop rows with invalid 'publishedAt' dates
    df = df.dropna(subset=['publishedAt'])

    # Filter based on date range
    mask = (df['publishedAt'] >= start_date) & (df['publishedAt'] <= end_date)
    filtered_df = df.loc[mask].copy()

    return filtered_df

def filter_videos_by_keyword(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    Filters the DataFrame to include only videos whose title contains the keyword.
    
    Args:
        df (pd.DataFrame): DataFrame containing videos or shorts.
        keyword (str): Keyword to search for in titles.
    
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    if df.empty or not keyword:
        return df
    
    # Case-insensitive search in title
    mask = df['title'].str.contains(keyword, case=False, na=False)
    filtered_df = df.loc[mask].copy()
    
    return filtered_df

#if __name__ == "__main__":
    #main()
