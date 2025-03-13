import datetime
import os
import subprocess
import shlex
import time
import xml.etree.ElementTree as ET
import requests

# Constants
EPG_URL = "https://raw.githubusercontent.com/ragetraxx/friendly-giggle/refs/heads/main/epg.xml"
EPG_FILE = "epg.xml"
OMDB_API_KEY = "a3b171bc"
OMDB_URL = "http://www.omdbapi.com/?apikey=" + OMDB_API_KEY
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"
EPG_REFRESH_INTERVAL = 21600  # Refresh EPG every 6 hours

def download_epg():
    """Download the latest EPG file from GitHub."""
    try:
        response = requests.get(EPG_URL, timeout=10)
        if response.status_code == 200:
            with open(EPG_FILE, "wb") as f:
                f.write(response.content)
            print("✅ EPG file updated successfully!")
        else:
            print(f"❌ ERROR: Failed to fetch EPG. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ ERROR: EPG download failed - {e}")

def get_movie_duration(title):
    """Fetch movie duration from OMDb API."""
    try:
        response = requests.get(OMDB_URL, params={"t": title})
        data = response.json()
        
        if "Runtime" in data:
            duration_str = data["Runtime"]  # Example: "120 min"
            duration_minutes = int(duration_str.split(" ")[0])
            return duration_minutes
        else:
            print(f"⚠️ WARNING: Could not fetch duration for '{title}', defaulting to 2 hours.")
            return 120  # Default to 2 hours if duration is not found

    except requests.RequestException as e:
        print(f"❌ ERROR: Failed to fetch movie duration - {e}")
        return 120  # Default to 2 hours on error

def parse_epg():
    """Parse EPG XML to extract movie schedule."""
    if not os.path.exists(EPG_FILE):
        print(f"❌ ERROR: {EPG_FILE} not found!")
        return []

    try:
        tree = ET.parse(EPG_FILE)
        root = tree.getroot()
        movies = []

        for programme in root.findall("programme"):
            title = programme.find("title").text
            link_element = programme.find("link")
            url = link_element.text if link_element is not None else None

            if not url:
                continue

            # Fetch movie duration from OMDb
            duration_minutes = get_movie_duration(title)
            start_time_str = programme.get("start").split(" ")[0]
            start_time = datetime.datetime.strptime(start_time_str, "%Y%m%d%H%M%S")
            stop_time = start_time + datetime.timedelta(minutes=duration_minutes)

            movies.append({
                "title": title,
                "start_time": start_time,
                "stop_time": stop_time,
                "url": url,
                "duration": duration_minutes
            })

        return sorted(movies, key=lambda x: x["start_time"])

    except ET.ParseError:
        print("❌ ERROR: Failed to parse EPG XML!")
        return []

def get_current_movie(movies):
    """Find the movie that should be playing now."""
    now = datetime.datetime.utcnow()
    for movie in movies:
        if movie["start_time"] <= now < movie["stop_time"]:
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
    process = subprocess.Popen(command)

    # Wait for the movie duration before stopping the process
    time.sleep(movie["duration"] * 60)
    process.terminate()

def main():
    """Main loop to refresh EPG and stream movies continuously."""
    last_epg_update = 0

    while True:
        now = time.time()

        # Refresh EPG every 6 hours
        if now - last_epg_update >= EPG_REFRESH_INTERVAL:
            download_epg()
            last_epg_update = now

        scheduled_movies = parse_epg()
        if not scheduled_movies:
            print("❌ ERROR: No movies found in EPG! Retrying in 5 minutes...")
            time.sleep(300)
            continue

        while True:
            movie = get_current_movie(scheduled_movies)
            if movie:
                stream_movie(movie)
            else:
                print("⏳ Waiting for the next scheduled movie...")
                time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
