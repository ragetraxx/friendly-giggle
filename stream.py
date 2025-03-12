import json
import random
import time
import subprocess
import shlex
import datetime
import os

MOVIE_FILE = "movies.json"
EPG_FILE = "epg.xml"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"
EPG_DURATION_HOURS = 6
MOVIES_PER_HOUR = 2  # Adjust based on movie length
TOTAL_MOVIES = EPG_DURATION_HOURS * MOVIES_PER_HOUR

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
        print("❌ ERROR: No movies available to create EPG!")
        return []

    start_time = datetime.datetime.utcnow()
    epg_data = """<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n"""
    selected_movies = random.sample(movies, min(TOTAL_MOVIES, len(movies)))  # Select movies without repeats

    schedule = []  # Store the exact order of movies

    for movie in selected_movies:
        start_str = start_time.strftime("%Y%m%d%H%M%S") + " +0000"
        end_time = start_time + datetime.timedelta(minutes=180)  # Approx. 3-hour runtime
        end_str = end_time.strftime("%Y%m%d%H%M%S") + " +0000"

        epg_data += f"""    <programme start="{start_str}" stop="{end_str}" channel="bihm">
        <title>{movie["title"]}</title>
        <desc>{movie.get("description", "No description available")}</desc>
    </programme>\n"""

        schedule.append(movie)  # Save movie order
        start_time = end_time  # Move to next time slot

    epg_data += "</tv>"

    with open(EPG_FILE, "w") as f:
        f.write(epg_data)

    if os.path.exists(EPG_FILE) and os.path.getsize(EPG_FILE) > 0:
        print(f"✅ SUCCESS: EPG generated with {len(schedule)} movies")
    else:
        print("❌ ERROR: EPG file is empty!")

    return schedule  # Return the exact movie schedule

def stream_movie(movie):
    """Stream a single movie using FFmpeg."""
    title = movie["title"]
    url = movie["url"]

    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
    overlay_text = shlex.quote(title)

    command = f"""
    ffmpeg -re -fflags nobuffer -rtbufsize 128M -probesize 10M -analyzeduration 1000000 \
    -threads 2 -i {video_url_escaped} -i {overlay_path_escaped} \
    -filter_complex "[1:v]scale2ref=w=main_w:h=main_h:force_original_aspect_ratio=decrease[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20,fps=30" \
    -c:v libx264 -preset fast -tune zerolatency -b:v 2500k -maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 50 \
    -c:a aac -b:a 192k -ar 48000 -f flv {shlex.quote(RTMP_URL)}
    """

    print(f"🎬 Now Streaming: {title}")
    subprocess.run(command, shell=True)

def main():
    """Main function to generate EPG and stream movies."""
    movies = load_movies()
    scheduled_movies = generate_epg(movies)  # Generate EPG and get exact schedule

    if not scheduled_movies:
        print("❌ ERROR: No movies scheduled to stream!")
        return

    for movie in scheduled_movies:
        stream_movie(movie)

if __name__ == "__main__":
    main()
