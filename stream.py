import os
import json
import subprocess
import time

# ✅ Configuration
PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")  # Get RTMP_URL from GitHub Secret
OVERLAY = os.path.abspath("overlay.png")  # Use absolute path for overlay
MAX_RETRIES = 3  # Retry attempts if no movies are found
RETRY_DELAY = 60  # Time (seconds) before retrying if no movies are found

# ✅ Check if RTMP_URL is set
if not RTMP_URL:
    print("❌ ERROR: RTMP_URL environment variable is NOT set! Check GitHub Secrets.")
    exit(1)

# ✅ Ensure required files exist
if not os.path.exists(PLAY_FILE):
    print(f"❌ ERROR: {PLAY_FILE} not found!")
    exit(1)

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
    """Stream a single movie using FFmpeg and wait for it to finish."""
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
        "-rtbufsize", "8M",  # ✅ Lower buffer to prevent excess latency
        "-probesize", "32M",
        "-analyzeduration", "32M",
        "-i", url,
        "-i", OVERLAY,
        "-filter_complex",
        "[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,"  # ✅ Correct overlay positioning
        f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=20:x=30:y=30",
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
        RTMP_URL,
        "-loglevel", "error",  # ✅ Show only errors, not all logs
    ]

    print(f"🎬 Now Streaming: {title}")
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # ✅ Wait for FFmpeg to finish before playing the next movie
        for line in process.stderr:
            print(line, end="")

        process.wait()

    except Exception as e:
        print(f"❌ ERROR: FFmpeg failed for '{title}' - {str(e)}")

def main():
    """Main function to stream all movies in sequence."""
    retry_attempts = 0

    while retry_attempts < MAX_RETRIES:
        movies = load_movies()

        if not movies:
            retry_attempts += 1
            print(f"❌ ERROR: No movies available! Retrying ({retry_attempts}/{MAX_RETRIES}) in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            continue

        retry_attempts = 0  # Reset retry counter on success

        while True:
            for movie in movies:
                stream_movie(movie)  # ✅ This will now wait for each movie to finish before starting the next one
                print("🔄 Movie ended. Playing next movie...")

            print("🔄 All movies played, restarting from the beginning...")

    print("❌ ERROR: Maximum retry attempts reached. Exiting.")

if __name__ == "__main__":
    main()
