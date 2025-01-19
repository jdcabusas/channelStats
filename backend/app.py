import sys
import pandas as pd
from get_top_videos import get_channel_videos_and_shorts
from datetime import datetime, timezone

# ==============================
#    CONFIGURATION
# ==============================
YOUTUBE_API_KEY = "AIzaSyDkT74UC9iq4pFcCvXqTzPgAGhLT0Uo6bo"  # Replace with your actual YouTube Data API key

# ==============================
#    COMMAND-LINE INTERFACE
# ==============================
def get_videos(channel_url, start_date_str, end_date_str):
    """
    Entry point when running from command line.
    Usage:
      python app.py <channel_url> <start_date> <end_date>
    Example:
      python app.py "https://www.youtube.com/@SomeChannel" 2024-01-01 2024-04-01
    """
    #if len(sys.argv) != 4:
    #    print("Usage: python app.py <channel_url> <start_date> <end_date>")
    #    print("Example: python app.py \"https://www.youtube.com/@SomeChannel\" 2024-01-01 2024-04-01")
    #    sys.exit(1)

    #channel_url = sys.argv[1]
    #start_date_str = sys.argv[2]
    #end_date_str = sys.argv[3]

    print(f"Fetching videos for channel URL: {channel_url}\n")

    # Parse and validate the dates
    try:
        start_date = pd.to_datetime(start_date_str, format="%Y-%m-%d", utc=True)
    except ValueError:
        print("Error: Start date is not in the correct format (YYYY-MM-DD).")
        sys.exit(1)

    try:
        end_date = pd.to_datetime(end_date_str, format="%Y-%m-%d", utc=True) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    except ValueError:
        print("Error: End date is not in the correct format (YYYY-MM-DD).")
        sys.exit(1)

    if end_date < start_date:
        print("Error: End date cannot be earlier than start date.")
        sys.exit(1)

    # Fetch videos and shorts DataFrames
    df_videos, df_shorts = get_channel_videos_and_shorts(channel_url, YOUTUBE_API_KEY)

    # Log total videos retrieved
    print(f"Total Videos Retrieved: {len(df_videos)}, Shorts Retrieved: {len(df_shorts)}\n")

    # Filter DataFrames based on date range
    df_videos_filtered = filter_videos_by_date(df_videos, start_date, end_date)
    df_shorts_filtered = filter_videos_by_date(df_shorts, start_date, end_date)

    # Log how many videos are within the date range
    print(f"Videos within date range: {len(df_videos_filtered)}, Shorts within date range: {len(df_shorts_filtered)}\n")

    # Sort filtered DataFrames by viewCount descending
    df_videos_sorted = df_videos_filtered.sort_values(by="viewCount", ascending=False).reset_index(drop=True)
    df_shorts_sorted = df_shorts_filtered.sort_values(by="viewCount", ascending=False).reset_index(drop=True)

    # Display the top 15 most viewed videos and shorts within the date range
    print(f"=== Top 15 Videos by View Count from {start_date.date()} to {end_date.date()} ===")
    if not df_videos_sorted.empty:
        print(df_videos_sorted.head(15)[['title', 'viewCount', 'url', 'publishedAt']].to_string(index=False))
    else:
        print("No normal videos found within this date range.")

    print(f"\n=== Top 15 Shorts by View Count from {start_date.date()} to {end_date.date()} ===")
    if not df_shorts_sorted.empty:
        print(df_shorts_sorted.head(15)[['title', 'viewCount', 'url', 'publishedAt']].to_string(index=False))
    else:
        print("No shorts found within this date range.")

    # Optional: Save to CSV
    # Uncomment the following lines if you wish to save the DataFrames
    # df_videos_sorted.to_csv("filtered_videos.csv", index=False)
    # df_shorts_sorted.to_csv("filtered_shorts.csv", index=False)
    # print("\nFiltered DataFrames saved to 'filtered_videos.csv' and 'filtered_shorts.csv'.")

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

#if __name__ == "__main__":
    #main()
