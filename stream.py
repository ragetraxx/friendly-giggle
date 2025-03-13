import os
import time
import json
import shlex
import requests
import subprocess
from datetime import datetime, timedelta

# Constants
MOVIES_JSON_URL = "https://raw.githubusercontent.com/ragetraxx/friendly-giggle/main/movies.json"
EPG_FILE = "epg.xml"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OMDB_API_KEY = "a3b171bc"  # API key for OMDB
OVERLAY = "overlay.png"  # Path to overlay image

# Function to fetch movie duration from OMDB
def get_movie_duration(title):
    query = f"http://www.omdbapi.com/?t={shlex.quote(title)}&apikey={OMDB_API_KEY}"
    response = requests.get(query)
    data = response.json()

    if "Runtime" in data:
        try:
            return int(data["Runtime"].split()[0])  # Extract minutes
        except ValueError:
            pass
    
    return 120  # Default duration if not found

# Function to generate epg.xml
def generate_epg(movies):
    if not movies:
        print("⚠️ No movies found for EPG generation!")
        return
    
    start_time = datetime.utcnow()
    epg_content = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n'

    for movie in movies:
        title = movie["title"]
        image = movie["image"]
        url = movie["url"]
        duration = get_movie_duration(title)

        stop_time = start_time + timedelta(minutes=duration)

        print(f"📅 Adding to EPG: {title} | Start: {start_time} | Stop: {stop_time}")

        epg_content += f"""    <programme start="{start_time.strftime('%Y%m%d%H%M%S')} +0000" stop="{stop_time.strftime('%Y%m%d%H%M%S')} +0000" channel="bihm">
        <title>{title}</title>
        <desc>Film Library</desc>
        <icon src="{image}"/>
        <link>{url}</link>
    </programme>\n"""
        
        start_time = stop_time

    epg_content += "</tv>"

    print("📂 Generated EPG Content:\n", epg_content)

    with open(EPG_FILE, "w", encoding="utf-8") as file:
        file.write(epg_content)

    print("✅ EPG.xml updated successfully!")

# Function to start streaming
def start_stream(url, title):
    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
    
    # Fix colon issue in title
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg",
        "-re",
        "-fflags", "+genpts",
        "-rtbufsize", "128M",
        "-probesize", "10M",
        "-analyzeduration", "1000000",
        "-i", video_url_escaped,
        "-i", overlay_path_escaped,
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

    print(f"🎬 Now Streaming: {title}")
    subprocess.run(command)

# Function to fetch movies from JSON
def fetch_movies():
    try:
        response = requests.get(MOVIES_JSON_URL)
        movies = response.json()
        return movies if movies else []
    except Exception as e:
        print(f"❌ Error fetching movies: {e}")
        return []

# Main loop to update EPG and stream movies
def main():
    while True:
        print("🔄 Fetching new movie list...")
        movies = fetch_movies()

        if not movies:
            print("⚠️ No movies found! Retrying in 10 minutes...")
            time.sleep(600)
            continue

        print("📺 Generating EPG...")
        generate_epg(movies)

        for movie in movies:
            title = movie["title"]
            url = movie["url"]
            duration = get_movie_duration(title) * 60  # Convert to seconds

            print(f"🎥 Streaming: {title} for {duration // 60} minutes")
            start_stream(url, title)

            print("⏳ Waiting for next movie...")
            time.sleep(duration)

        print("🔄 Restarting the cycle in 6 hours...")
        time.sleep(21600)  # 6 hours

if __name__ == "__main__":
    main()
