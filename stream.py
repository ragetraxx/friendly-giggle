import os
import json
import time
import requests
import shlex
import subprocess
from datetime import datetime, timedelta

# === CONFIGURATION ===
MOVIES_JSON_URL = "https://raw.githubusercontent.com/ragetraxx/friendly-giggle/main/movies.json"
EPG_FILE = "epg.xml"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OMDB_API_KEY = "a3b171bc"
OVERLAY = "overlay.png"  # Update with actual overlay image path

# === FUNCTION TO FETCH MOVIES ===
def fetch_movies():
    try:
        response = requests.get(MOVIES_JSON_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Failed to fetch movies. Status Code: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching movies: {e}")
        return []

# === FUNCTION TO GET MOVIE DURATION ===
def get_movie_duration(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url).json()
        duration = response.get("Runtime", "90 min")  # Default to 90 minutes
        return int(duration.split(" ")[0])  # Extract number
    except Exception as e:
        print(f"⚠️ Failed to get duration for {title}: {e}")
        return 90  # Default to 90 minutes

# === FUNCTION TO GENERATE EPG ===
def generate_epg(movies):
    start_time = datetime.utcnow()
    epg_content = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n'
    
    for movie in movies:
        title = movie["title"]
        image = movie["image"]
        url = movie["url"]
        duration = get_movie_duration(title)  # Get duration in minutes
        stop_time = start_time + timedelta(minutes=duration)

        epg_content += f"""    <programme start="{start_time.strftime('%Y%m%d%H%M%S')} +0000" stop="{stop_time.strftime('%Y%m%d%H%M%S')} +0000" channel="bihm">
        <title>{title}</title>
        <desc>Film Library</desc>
        <icon src="{image}"/>
        <link>{url}</link>
    </programme>\n"""
        
        start_time = stop_time  # Set new start time

    epg_content += "</tv>"
    
    with open(EPG_FILE, "w") as file:
        file.write(epg_content)

    print("✅ EPG.xml updated!")

# === FUNCTION TO STREAM MOVIE ===
def stream_movie(url, title):
    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
    
    # Fix title formatting
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

# === MAIN LOOP ===
while True:
    movies = fetch_movies()
    
    if not movies:
        print("⚠️ No movies found. Retrying in 10 minutes...")
        time.sleep(600)
        continue

    generate_epg(movies)  # Update EPG.xml

    for movie in movies:
        stream_movie(movie["url"], movie["title"])
        time.sleep(5)  # Short delay before next movie
