import json
import datetime
import os
import subprocess
import shlex
import time
import xml.etree.ElementTree as ET

EPG_FILE = "epg.xml"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"
MAX_RETRIES = 3  # Retry limit if no valid movies are found

def parse_epg():
    """Parse EPG XML to extract scheduled movies and their start times."""
    if not os.path.exists(EPG_FILE):
        print(f"❌ ERROR: {EPG_FILE} not found!")
        return []

    try:
        tree = ET.parse(EPG_FILE)
        root = tree.getroot()
        movies = []

        for programme in root.findall("programme"):
            start_time_str = programme.get("start").split(" ")[0]
            start_time = datetime.datetime.strptime(start_time_str, "%Y%m%d%H%M%S")

            title = programme.find("title").text
            link_element = programme.find("link")
            url = link_element.text if link_element is not None else None

            if url:
                movies.append({"title": title, "start_time": start_time, "url": url})

        return sorted(movies, key=lambda x: x["start_time"])
    
    except ET.ParseError:
        print("❌ ERROR: Failed to parse EPG XML!")
        return []

def get_current_movie(movies):
    """Find the movie that should be playing based on the current time."""
    now = datetime.datetime.utcnow()
    for movie in movies:
        if movie["start_time"] <= now:
            return movie
    return None

def stream_movie(movie):
    """Stream the selected movie using FFmpeg."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg",
        "-re",
        "-fflags", "+genpts",
        "-rtbufsize", "128M",
        "-probesize", "10M",
        "-analyzeduration", "1000000",
        "-i", shlex.quote(url),
        "-i", shlex.quote(OVERLAY),
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
    """Main function to ensure EPG-based streaming."""
    retry_attempts = 0

    while retry_attempts < MAX_RETRIES:
        scheduled_movies = parse_epg()

        if not scheduled_movies:
            retry_attempts += 1
            print(f"❌ ERROR: No movies found in EPG! Retrying ({retry_attempts}/{MAX_RETRIES})...")
            time.sleep(60)
            continue

        retry_attempts = 0  # Reset retry counter on success

        while True:
            movie = get_current_movie(scheduled_movies)
            if movie:
                stream_movie(movie)
            else:
                print("⏳ Waiting for the next scheduled movie...")
                time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
