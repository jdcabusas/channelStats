# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a YouTube Channel Statistics application that fetches and analyzes YouTube video performance data. It consists of a Python Flask backend that interfaces with the YouTube Data API and provides analytics through a REST API.

## Architecture
- **Backend**: Flask web server (`backend/server.py`) with YouTube Data API integration
- **Core Logic**: Video fetching and analysis in `backend/get_top_videos.py` and `backend/app.py`
- **Frontend**: Directory exists but appears to be empty/placeholder
- **API Endpoint**: `/get_data` accepts channel_url, start_date, end_date parameters
- **Containerized**: Dockerized backend with Python 3.11

## Development Commands

### Running the Backend
```bash
# Local development
cd backend
python server.py
# Server runs on http://localhost:5000

# Using Docker
cd backend
docker build -t channelstats .
docker run -p 5000:5000 channelstats
```

### Installing Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Testing the API
```bash
# Example API call (modify dates and channel as needed)
curl "http://localhost:5000/get_data?channel_url=https://www.youtube.com/@AlexHormozi&start_date=2024-01-01&end_date=2024-04-01"
```

## Key Components

### YouTube Data Integration
- **API Key**: Hardcoded in `get_top_videos.py:9` and `app.py:9` (consider moving to environment variables)
- **Channel ID Resolution**: Supports both handle-based URLs (`/@handle`) and standard channel URLs (`/channel/UC...`)
- **Video Classification**: Automatically separates regular videos from YouTube Shorts based on duration (<60 seconds)
- **Data Retrieved**: Title, publish date, view count, like count, comment count, duration

### API Structure
- **Endpoint**: `GET /get_data`
- **Parameters**: 
  - `channel_url` (required): YouTube channel URL
  - `start_date` (required): YYYY-MM-DD format
  - `end_date` (required): YYYY-MM-DD format
- **Response**: JSON with `top_videos` and `top_shorts` arrays, sorted by view count

### Data Processing
- Videos are filtered by date range and sorted by view count descending
- Separate handling for regular videos vs YouTube Shorts
- Returns pandas DataFrames converted to JSON format

## Dependencies
- `pandas`: Data manipulation and analysis
- `requests`: HTTP requests to YouTube API
- `flask`: Web framework
- `flask_cors`: Cross-origin resource sharing

## Important Notes
- YouTube Data API key is currently hardcoded - consider using environment variables for production
- The frontend directory is empty and may need implementation
- Server is configured to run on all interfaces (0.0.0.0:5000) for containerization