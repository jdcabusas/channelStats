CHANNEL_URL="https://www.youtube.com/@AlexHormozi"
START_DATE="2024-01-01"
END_DATE="2024-04-01"

curl "http://13.210.56.219:5000/get_data?channel_url=${CHANNEL_URL}&start_date=${START_DATE}&end_date=${END_DATE}"

