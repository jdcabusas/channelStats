import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from app import get_videos  # Import the new function
import pandas as pd

app = Flask(__name__)
CORS(app)

# If you're using Flask-Dotenv for environment variables
#from dotenv import load_dotenv
#load_dotenv()

@app.route('/')
def index():
    return "Connected to app"

@app.route('/get_data', methods=['GET'])
def get_data():
    """
    Endpoint to retrieve top videos and shorts with optional date range and keyword filtering.

    Query Parameters:
        channel_url (str): URL of the YouTube channel.
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
        keyword (str, optional): Keyword to search in title and description.

    Returns:
        JSON response with top videos and shorts.
    """
    # Extract query parameters
    channel_url = request.args.get('channel_url')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    keyword = request.args.get('keyword')

    # Validate parameters
    if not channel_url:
        return jsonify({"error": "Missing required parameter: channel_url"}), 400

    # Call the process_videos function
    try:
        df_videos_sorted, df_shorts_sorted = get_videos(channel_url, start_date, end_date, keyword)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

    # Convert DataFrames to JSON serializable format
    videos_json = df_videos_sorted.to_dict(orient='records')
    shorts_json = df_shorts_sorted.to_dict(orient='records')

    # Return the data as JSON
    return jsonify({
        "top_videos": videos_json,
        "top_shorts": shorts_json
    }), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

