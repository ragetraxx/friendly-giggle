import os
import time
import json
import shlex
import requests
import subprocess
from datetime import datetime

# Constants
MOVIES_JSON_URL = "https://raw.githubusercontent.com/ragetraxx/friendly-giggle/main/movies.json"
NOW_SHOWING_FILE = "now_showing.json"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OMDB_API_KEY = "a3b171bc"
OVERLAY = "overlay.png"

# Function to fetch movie duration from OMDB
def get_movie_duration(title):
    try:
        query = f"http://www.omdbapi.com/?t={shlex.quote(title)}&apikey={OMDB_API_KEY}"
        response = requests.get(query)
        data = response.json()

        if "Runtime" in data:
            return int(data["Runtime"].split()[0])  # Extract minutes
    except Exception as e:
        print(f"❌ OMDB API Error: {e}")

    return 120  # Default duration if API fails

# Function to generate now_showing.json
def generate_now_showing(movies):
    if not movies:
        print("⚠️ No movies found!")
        return
    
    selected_movie = movies[0]  # Pick the first movie
    title = selected_movie["title"]
    url = selected_movie["url"]
    duration = get_movie_duration(title)

    now_showing_data = {
        "title": title,
        "url": url,
        "duration": duration
    }

    with open(NOW_SHOWING_FILE, "w", encoding="utf-8") as file:
        json.dump(now_showing_data, file, indent=4)

    print(f"✅ Updated {NOW_SHOWING_FILE}: {now_showing_data}")

# Function to start streaming
def start_stream(url, title):
    print(f"🎬 Now Streaming: {title}")
    print(f"🔗 Video URL: {url}")
    print(f"📡 Streaming to: {RTMP_URL}")

    video_url_escaped = shlex.quote(url)
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg",
        "-re",
        "-fflags", "+genpts",
        "-rtbufsize", "128M",
        "-probesize", "10M",
        "-analyzeduration", "1000000",
        "-i", video_url_escaped,
        "-i", OVERLAY,
        "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,"
        f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-b:v", "2500k",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-pix_fmt", "yuv420p",
        "-g", "50",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-f", "flv",
        RTMP_URL
    ]

    print("🚀 Running FFMPEG command...")
    subprocess.run(command)

# Function to fetch movies
def fetch_movies():
    try:
        response = requests.get(MOVIES_JSON_URL)
        movies = response.json()
        if not movies:
            print("⚠️ No movies found in JSON!")
        return movies
    except Exception as e:
        print(f"❌ Error fetching movies: {e}")
        return []

# Main execution
def main():
    print("🔄 Fetching movies...")
    movies = fetch_movies()

    if not movies:
        print("⚠️ No movies found! Exiting...")
        return

    print("📺 Generating now_showing.json...")
    generate_now_showing(movies)

    # Read now_showing.json
    with open(NOW_SHOWING_FILE, "r", encoding="utf-8") as file:
        now_showing = json.load(file)

    title = now_showing["title"]
    url = now_showing["url"]
    duration = now_showing["duration"] * 60  # Convert to seconds

    print(f"🎥 Streaming: {title} for {duration // 60} minutes")
    start_stream(url, title)

if __name__ == "__main__":
    main()
