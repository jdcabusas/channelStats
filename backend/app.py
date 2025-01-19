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
    print(f"Fetching videos for channel URL: {channel_url}\n")

    # Fetch videos and shorts DataFrames
    df_videos, df_shorts = get_channel_videos_and_shorts(channel_url, YOUTUBE_API_KEY)

    # Log total videos retrieved
    print(f"Total Videos Retrieved: {len(df_videos)}, Shorts Retrieved: {len(df_shorts)}\n")

    # Prompt user for date range
    start_date, end_date = prompt_for_dates()
    
    # Display Top Videos
    if not df_shorts.empty:
        print("=== Top Videos by View Count ===")
        print(df_videos[['title', 'viewCount', 'url']].head(15).to_string(index=False))
    else:
        print("No shorts found.")

    # Display Top 5 Shorts
    if not df_shorts.empty:
        print("=== Top Shorts by View Count ===")
        print(df_shorts[['title', 'viewCount', 'url']].head(15).to_string(index=False))
    else:
        print("No shorts found.")


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

    # Save to CSV
    #df_videos_sorted.to_csv("filtered_videos.csv", index=False)
    #df_shorts_sorted.to_csv("filtered_shorts.csv", index=False)
    print("\nFiltered DataFrames saved to 'filtered_videos.csv' and 'filtered_shorts.csv'.")

def prompt_for_dates():
    """
    Prompts the user to input a start date and an end date.
    Ensures that the dates are in the correct format and that start_date <= end_date.
    
    Returns:
        (start_date, end_date): Tuple of timezone-aware datetime objects in UTC
    """
    while True:
        try:
            start_date_str = input("Enter start date (YYYY-MM-DD): ").strip()
            start_date = pd.to_datetime(start_date_str, format="%Y-%m-%d", utc=True)
            break
        except ValueError:
            print("Invalid start date format. Please use YYYY-MM-DD.")

    while True:
        try:
            end_date_str = input("Enter end date (YYYY-MM-DD): ").strip()
            end_date = pd.to_datetime(end_date_str, format="%Y-%m-%d", utc=True)
            if end_date < start_date:
                print("End date cannot be earlier than start date. Please re-enter.")
                continue
            # To include the entire end date, set it to the end of the day
            end_date = end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            break
        except ValueError:
            print("Invalid end date format. Please use YYYY-MM-DD.")

    return start_date, end_date

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

if __name__ == "__main__":
    main()

