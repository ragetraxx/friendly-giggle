import json
import os
import subprocess
import shlex
import time
import random

PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")  # Load RTMP URL from environment variable
OVERLAY = "overlay.png"
MAX_RETRIES = 3  # Maximum retry attempts if no movies are found

# Check if RTMP_URL is set
if not RTMP_URL:
    print("❌ ERROR: RTMP_URL environment variable is not set!")
    exit(1)

# Ensure play.json exists
if not os.path.exists(PLAY_FILE):
    print(f"❌ ERROR: {PLAY_FILE} not found!")
    exit(1)

# Ensure overlay image exists
if not os.path.exists(OVERLAY):
    print(f"❌ ERROR: Overlay image '{OVERLAY}' not found!")
    exit(1)

def load_movies():
    """Load movies from play.json."""
    try:
        with open(PLAY_FILE, "r") as f:
            movies = json.load(f)
            if not movies:
                print("❌ ERROR: play.json is empty!")
                return []
            return movies
    except json.JSONDecodeError:
        print("❌ ERROR: Failed to parse play.json! Check for syntax errors.")
        return []

def stream_movie(movie):
    """Stream a single movie using FFmpeg."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    # Escape values for safe execution
    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg",
        "-re",
        "-fflags", "+genpts",
        "-rtbufsize", "32M",
        "-probesize", "1M",
        "-analyzeduration", "500000",
        "-i", url,  # Direct URL instead of escaped version
        "-i", OVERLAY,
        "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,"
        f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20",
        "-c:v", "libx264",
        "-preset", "fast",
        "-tune", "film",
        "-b:v", "4000k",
        "-crf", "23",
        "-maxrate", "4500k",
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

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: FFmpeg failed for '{title}'\n{e.stderr}")

def main():
    """Main function to randomly pick and stream movies."""
    retry_attempts = 0

    while retry_attempts < MAX_RETRIES:
        movies = load_movies()

        if not movies:
            retry_attempts += 1
            print(f"❌ ERROR: No movies available! Retrying ({retry_attempts}/{MAX_RETRIES})...")
            time.sleep(60)
            continue

        retry_attempts = 0  # Reset retry counter on success

        while True:
            movie = random.choice(movies)  # Pick a random movie from play.json
            stream_movie(movie)

            print("🔄 Picking a new random movie...")

    print("❌ ERROR: Maximum retry attempts reached. Exiting.")

if __name__ == "__main__":
    main()
