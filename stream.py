import os
import json
import subprocess
import time

# ✅ Configuration
PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")  # Get RTMP_URL from environment variable
OVERLAY = os.path.abspath("overlay.png")  # Use absolute path for overlay
RETRY_DELAY = 60  # Time (seconds) before retrying if no movies are found

# ✅ Check if RTMP_URL is set
if not RTMP_URL:
    print("❌ ERROR: RTMP_URL environment variable is NOT set! Check configuration.")
    exit(1)

# ✅ Ensure required files exist
if not os.path.exists(PLAY_FILE):
    print(f"❌ ERROR: {PLAY_FILE} not found!")
    exit(1)

if not os.path.exists(OVERLAY):
    print(f"❌ ERROR: Overlay image '{OVERLAY}' not found!")
    exit(1)

def load_next_movie():
    """Load the next movie from play.json."""
    try:
        with open(PLAY_FILE, "r") as f:
            movies = json.load(f)
            if not movies:
                print("❌ ERROR: play.json is empty!")
                return None
            return movies.pop(0)  # Return the first movie and remove it from the list
    except json.JSONDecodeError:
        print("❌ ERROR: Failed to parse play.json! Check for syntax errors.")
        return None

def stream_movie(movie):
    """Stream a single movie using FFmpeg with minimal buffering for smooth playback."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')
    
    command = [
        "ffmpeg", "-re", "-fflags", "nobuffer", "-i", url, "-i", OVERLAY, "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=20:x=30:y=30",
        "-c:v", "libx264", "-profile:v", "main", "-preset", "veryfast", "-tune", "zerolatency", "-b:v", "2800k",
        "-maxrate", "2800k", "-bufsize", "4000k", "-pix_fmt", "yuv420p", "-g", "50", "-vsync", "cfr",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-f", "flv", "-rtmp_live", "live", RTMP_URL, "-loglevel", "info"
    ]
    
    print(f"🎬 Now Streaming: {title}")
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            print(line, end="")
        process.wait()
    except Exception as e:
        print(f"❌ ERROR: FFmpeg failed for '{title}' - {str(e)}")

def main():
    """Main function to continuously stream movies live."""
    while True:
        movie = load_next_movie()
        if not movie:
            print(f"❌ ERROR: No movies available! Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            continue
        stream_movie(movie)
        print("🔄 Movie ended. Checking for new content...")

if __name__ == "__main__":
    main()
