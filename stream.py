import json
import subprocess
import shlex
import time
from datetime import datetime

# RTMP Destination
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"

# Overlay Image Path
OVERLAY = "overlay.png"  # Ensure this file exists

# Load Now Showing Movies
def load_now_showing():
    try:
        with open("now_showing.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("❌ ERROR: now_showing.json not found!")
        return []
    except json.JSONDecodeError:
        print("❌ ERROR: now_showing.json is invalid!")
        return []

# Get the current playing movie based on the schedule
def get_current_movie(movies):
    now = datetime.now()

    for movie in movies:
        start_dt = datetime.strptime(movie["start_time"], "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(movie["end_time"], "%Y-%m-%d %H:%M:%S")

        if start_dt <= now < end_dt:
            return movie
    
    return None  # No movie is scheduled at this time

# Stream Movie
def stream_video(url, title):
    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)

    # Fix special characters in title
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
    return subprocess.Popen(command)

# Continuous Streaming Loop
def main():
    movies = load_now_showing()
    if not movies:
        print("❌ No movies found in now_showing.json!")
        return

    current_process = None
    current_movie = None

    while True:
        now_movie = get_current_movie(movies)

        if now_movie:
            if current_movie != now_movie:
                if current_process:
                    current_process.terminate()
                    current_process.wait()

                title = now_movie["title"]
                url = now_movie["url"]
                print(f"▶️ Switching to: {title}")

                current_process = stream_video(url, title)
                current_movie = now_movie
        else:
            print("⏳ No movie scheduled, waiting...")
            time.sleep(30)  # Check again in 30 seconds

        time.sleep(10)  # Check for schedule changes every 10 seconds

# Run the script
if __name__ == "__main__":
    main()
