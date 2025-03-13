import json
import random
import datetime
import os
import subprocess
import shlex
import time

MOVIE_FILE = "movies.json"
EPG_FILE = "epg.xml"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"
EPG_DURATION_HOURS = 6
MOVIES_PER_HOUR = 2  # Adjust based on movie length
TOTAL_MOVIES = EPG_DURATION_HOURS * MOVIES_PER_HOUR
MAX_RETRIES = 3  # Maximum retry attempts if no movies are found

def load_movies():
    """Load movies from JSON file."""
    if not os.path.exists(MOVIE_FILE):
        print(f"❌ ERROR: {MOVIE_FILE} not found!")
        return []

    with open(MOVIE_FILE, "r") as f:
        try:
            movies = json.load(f)
            if not movies:
                print("❌ ERROR: movies.json is empty!")
            return movies
        except json.JSONDecodeError:
            print("❌ ERROR: Failed to parse movies.json!")
            return []

def generate_epg(movies):
    """Generate a new EPG XML file for the next 6 hours with selected movies."""
    if not movies:
        print("❌ ERROR: No movies available for EPG!")
        return []

    start_time = datetime.datetime.utcnow()
    epg_data = """<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n"""

    total_movies = min(TOTAL_MOVIES, len(movies))
    if total_movies == 0:
        print("❌ ERROR: No movies available to create EPG!")
        return []

    selected_movies = random.sample(movies, total_movies)
    schedule = []

    for movie in selected_movies:
        start_str = start_time.strftime("%Y%m%d%H%M%S +0000")
        end_time = start_time + datetime.timedelta(minutes=180)  # Approx. 3-hour runtime
        end_str = end_time.strftime("%Y%m%d%H%M%S +0000")

        epg_data += f"""    <programme start="{start_str}" stop="{end_str}" channel="bihm">
        <title>{movie["title"]}</title>
        <desc>{movie.get("description", "No description available")}</desc>
    </programme>\n"""

        schedule.append(movie)
        start_time = end_time  

    epg_data += "</tv>"

    with open(EPG_FILE, "w") as f:
        f.write(epg_data)

    if os.path.exists(EPG_FILE) and os.path.getsize(EPG_FILE) > 0:
        print(f"✅ SUCCESS: EPG generated with {len(schedule)} movies")
    else:
        print("❌ ERROR: EPG file is empty after writing!")

    return schedule  

def stream_movie(movie):
    """Stream a single movie using FFmpeg."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
    overlay_text = shlex.quote(title)

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

def main():
    """Main function to generate EPG and stream movies."""
    retry_attempts = 0

    while retry_attempts < MAX_RETRIES:
        movies = load_movies()
        scheduled_movies = generate_epg(movies)  # Generate EPG before streaming

        if not scheduled_movies:
            retry_attempts += 1
            print(f"❌ ERROR: No movies scheduled to stream! Retrying ({retry_attempts}/{MAX_RETRIES})...")
            time.sleep(60)
            continue

        retry_attempts = 0  # Reset retry counter on success

        for movie in scheduled_movies:
            stream_movie(movie)

        print("🔄 Regenerating EPG after 6 hours...")
        time.sleep(EPG_DURATION_HOURS * 3600)  # Wait 6 hours before regenerating EPG

    print("❌ ERROR: Maximum retry attempts reached. Exiting.")

if __name__ == "__main__":
    main()
