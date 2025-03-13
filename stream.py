import os
import time
import json
import shlex
import requests
import subprocess
from datetime import datetime, timedelta

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

# Function to schedule movies
def generate_schedule(movies):
    if not movies:
        print("⚠️ No movies found!")
        return

    current_time = datetime.utcnow()

    # Try to read the last schedule
    if os.path.exists(NOW_SHOWING_FILE):
        with open(NOW_SHOWING_FILE, "r", encoding="utf-8") as file:
            try:
                schedule_data = json.load(file)
                last_movie_end = datetime.strptime(schedule_data[-1]["end_time"], "%Y-%m-%d %H:%M:%S")

                # If the last movie is still playing, keep the schedule
                if current_time < last_movie_end:
                    print("⏳ Keeping current schedule...")
                    return schedule_data
            except:
                pass

    print("📅 Generating new schedule...")

    schedule = []
    next_start_time = current_time.replace(second=0, microsecond=0)  # Align to the nearest minute

    for movie in movies:
        title = movie["title"]
        url = movie["url"]
        duration = get_movie_duration(title)

        end_time = next_start_time + timedelta(minutes=duration)

        schedule.append({
            "title": title,
            "url": url,
            "duration": duration,
            "start_time": next_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
        })

        next_start_time = end_time  # Set next movie start time

    with open(NOW_SHOWING_FILE, "w", encoding="utf-8") as file:
        json.dump(schedule, file, indent=4)

    print(f"✅ Updated {NOW_SHOWING_FILE} with scheduled movies")
    return schedule

# Function to find the currently playing movie
def get_current_movie(schedule):
    current_time = datetime.utcnow()

    for movie in schedule:
        start_time = datetime.strptime(movie["start_time"], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(movie["end_time"], "%Y-%m-%d %H:%M:%S")

        if start_time <= current_time < end_time:
            return movie

    return None  # No movie found

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

    print("📅 Generating schedule...")
    schedule = generate_schedule(movies)

    if not schedule:
        print("⚠️ Error generating schedule!")
        return

    current_movie = get_current_movie(schedule)

    if not current_movie:
        print("⚠️ No movie currently scheduled to play!")
        return

    title = current_movie["title"]
    url = current_movie["url"]

    print(f"🎥 Now Playing: {title}")
    start_stream(url, title)

if __name__ == "__main__":
    main()
