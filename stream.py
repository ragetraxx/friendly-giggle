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
EPG_REFRESH_INTERVAL = 21600  # 6 hours

def download_epg():
    """Download the latest EPG file."""
    try:
        response = requests.get(EPG_URL, timeout=10)
        if response.status_code == 200:
            with open(EPG_FILE, "wb") as f:
                f.write(response.content)
            print("✅ EPG file updated!")
        else:
            print("⚠️ Failed to download EPG.")
    except requests.RequestException as e:
        print(f"❌ ERROR: {e}")

def get_current_movie():
    """Parse EPG and get the current movie."""
    if not os.path.exists(EPG_FILE):
        print("⚠️ EPG file missing. Downloading...")
        download_epg()

    try:
        tree = ET.parse(EPG_FILE)
        root = tree.getroot()
        now = datetime.datetime.utcnow()
        
        for programme in root.findall("programme"):
            start_time = datetime.datetime.strptime(programme.get("start")[:14], "%Y%m%d%H%M%S")
            stop_time = datetime.datetime.strptime(programme.get("stop")[:14], "%Y%m%d%H%M%S")

            if start_time <= now <= stop_time:
                return {
                    "title": programme.find("title").text,
                    "url": programme.find("link").text,
                    "icon": programme.find("icon").get("src")
                }
        
        print("⚠️ No movie found in EPG!")
    except Exception as e:
        print(f"❌ ERROR parsing EPG: {e}")

    return None

def stream_movie(title, url, icon):
    """Start streaming the movie."""
    print(f"🎬 Now Streaming: {title}")

    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
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

    while True:
        process = subprocess.Popen(command)
        process.wait()
        print("⚠️ Stream crashed! Restarting in 10 seconds...")
        time.sleep(10)

def main():
    """Main loop: update EPG, check movie, and stream."""
    last_epg_update = 0
    current_movie = None

    while True:
        now = time.time()

        if now - last_epg_update >= EPG_REFRESH_INTERVAL:
            download_epg()
            last_epg_update = now

        new_movie = get_current_movie()

        if new_movie and new_movie != current_movie:
            current_movie = new_movie
            stream_movie(current_movie["title"], current_movie["url"], current_movie["icon"])

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
