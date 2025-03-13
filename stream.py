import os
import time
import shlex
import subprocess
import requests
import xml.etree.ElementTree as ET

# Constants
EPG_URL = "https://raw.githubusercontent.com/ragetraxx/friendly-giggle/refs/heads/main/epg.xml"
EPG_FILE = "epg.xml"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"  # Change if your overlay image has a different path
FETCH_INTERVAL = 21600  # 6 hours in seconds

def fetch_epg():
    """Fetches the latest EPG XML file and saves it locally."""
    try:
        response = requests.get(EPG_URL, timeout=10)
        if response.status_code == 200:
            with open(EPG_FILE, "wb") as f:
                f.write(response.content)
            print("✅ EPG file updated successfully!")
        else:
            print(f"❌ Failed to fetch EPG. Status Code: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error fetching EPG: {e}")

def parse_epg():
    """Parses the EPG XML and extracts the next movie's title and streaming link."""
    if not os.path.exists(EPG_FILE):
        print("⚠️ No EPG file found. Fetching new one...")
        fetch_epg()

    try:
        tree = ET.parse(EPG_FILE)
        root = tree.getroot()
        programme = root.find("programme")

        if programme is not None:
            title = programme.find("title").text
            url = programme.find("link").text
            return title, url
        else:
            print("⚠️ No valid programme found in EPG.")
            return None, None
    except Exception as e:
        print(f"❌ Error parsing EPG: {e}")
        return None, None

def start_stream(title, url):
    """Starts the FFmpeg stream with overlay and title."""
    if not title or not url:
        print("⚠️ No valid movie found. Retrying in 10 minutes...")
        time.sleep(600)
        return

    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)

    # Fix the colon issue in the title
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

def main():
    """Main loop to update EPG and stream movies continuously."""
    while True:
        fetch_epg()
        title, url = parse_epg()
        if title and url:
            start_stream(title, url)
        print("⏳ Waiting 6 hours before fetching a new EPG...")
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    main()
