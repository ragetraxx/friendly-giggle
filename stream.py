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

    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')\
                    .replace("&", r"\&").replace("%", r"\%").replace("(", r"").replace(")", r"")
    
    command = [
    "ffmpeg",
    "-fflags", "+genpts",
    "-rtbufsize", "128M",  # Increased buffer size to handle high bitrates and prevent interruptions
    "-probesize", "128M",  # Increased probing size to ensure better handling of the stream
    "-analyzeduration", "128M",  # Increased analysis duration to avoid initial buffering
    "-i", url,  # The video URL
    "-i", OVERLAY,  # Overlay image
    "-filter_complex",
    "[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,"  # Correct overlay positioning
    f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=20:x=30:y=30",  # Overlay text
    "-c:v", "libx264",  # Use x264 codec for video
    "-preset", "fast",  # Speed optimization for streaming
    "-tune", "film",  # Tuned for film content, if you're streaming movies
    "-b:v", "2000k",  # Video bitrate, adjust depending on available bandwidth
    "-maxrate", "2500k",  # Max video bitrate, ensure this doesn't exceed your network capacity
    "-bufsize", "5000k",  # Buffer size for smooth streaming, should be higher than maxrate
    "-pix_fmt", "yuv420p",  # Pixel format for compatibility
    "-g", "30",  # Lower GOP size (keyframe interval) for better streaming continuity
    "-c:a", "aac",  # Audio codec
    "-b:a", "192k",  # Audio bitrate
    "-ar", "48000",  # Audio sample rate
    "-f", "flv",  # Format for RTMP
    RTMP_URL,  # RTMP URL for streaming
    "-loglevel", "info",  # Set log level for debugging and detailed logs
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
