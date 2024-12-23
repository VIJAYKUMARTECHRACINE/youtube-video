from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import mysql.connector

app = Flask(__name__)

# MySQL Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Vijay@9361",
    "database": "CMATamilwebDB"
}

# Video Download Directory
DOWNLOAD_FOLDER = './static/download'

# Your YouTube API Key
API_KEY = "AIzaSyCBlytCq1HF5baUq6bUibl2DJPJUChf8ew"
BASE_URL = "https://www.googleapis.com/youtube/v3"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/videos')
def get_videos():
    video_ids = ["TqkQLCBuucw", "3JZ_D3ELwOQ", "2Vv-BfVoq4g", "MB_CzIKKRg4", "-En7Ed4T2lU&t"]
    url = f"{BASE_URL}/videos?part=snippet,statistics&id={','.join(video_ids)}&key={API_KEY}"

    response = requests.get(url).json()
    videos=[]
    for item in response.get("items", []):
        videos.append({ "video_id": item["id"],
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
            "likes": item["statistics"].get("likeCount", "0"),
            "views": item["statistics"].get("viewCount", "0")})
    return jsonify(videos)

@app.route('/submit_info', methods=['POST'])
def submit_info():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    video_id = data.get('video_id')

    if not (name and phone and email and video_id):
        return jsonify({"error": "All fields are required."}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_info (name, phone, email, video_id) VALUES (%s, %s, %s, %s)",
            (name, phone, email, video_id),
        )
        conn.commit()
        return jsonify({"download_link": f"/download/{video_id}.mp4"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/download/<video_id>')
def download_video(video_id):
    return send_from_directory(DOWNLOAD_FOLDER, f"{video_id}", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True,port=5050)
