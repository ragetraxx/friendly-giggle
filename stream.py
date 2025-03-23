import os
import json
import subprocess
import time

PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")  # ✅ Get RTMP_URL from GitHub Secret
OVERLAY = "overlay.png"
MAX_RETRIES = 3  # ✅ Max retry attempts if movie fails

# ✅ Ensure RTMP_URL is set
if not RTMP_URL:
    print("❌ ERROR: RTMP_URL environment variable is NOT set! Check GitHub Secrets.")
    exit(1)

# ✅ Ensure required files exist
for file in [PLAY_FILE, OVERLAY]:
    if not os.path.exists(file):
        print(f"❌ ERROR: {file} not found!")
        exit(1)

def log_message(msg):
    """Log messages with timestamp."""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def load_movies():
    """Load movies from play.json."""
    try:
        with open(PLAY_FILE, "r") as f:
            movies = json.load(f)
            if not movies:
                log_message("❌ ERROR: play.json is empty!")
                return []
            return movies
    except json.JSONDecodeError:
        log_message("❌ ERROR: Failed to parse play.json! Check for syntax errors.")
        return []

def get_video_resolution(url):
    """Determine video resolution using FFprobe."""
    try:
        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json",
            url
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        video_info = json.loads(result.stdout)

        width = video_info["streams"][0]["width"]
        height = video_info["streams"][0]["height"]

        return width, height
    except Exception:
        return None, None

def stream_movie(movie):
    """Stream a movie using FFmpeg with SD to 4K handling."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        log_message(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    # ✅ Detect video resolution
    width, height = get_video_resolution(url)
    log_message(f"📺 Detected Resolution: {width}x{height}")

    # ✅ Set streaming parameters based on resolution
    if width and height:
        if width >= 3840 or height >= 2160:  # 4K
            maxrate = "12000k"
            bufsize = "16000k"
            scale_filter = "scale=1920:1080"  # ✅ Downscale to 1080p for stable streaming
        elif width >= 1920 or height >= 1080:  # 1080p
            maxrate = "8000k"
            bufsize = "12000k"
            scale_filter = "scale=1920:1080"
        elif width >= 1280 or height >= 720:  # 720p
            maxrate = "5000k"
            bufsize = "8000k"
            scale_filter = "scale=1280:720"
        else:  # SD
            maxrate = "3000k"
            bufsize = "5000k"
            scale_filter = "scale=854:480"
    else:
        log_message("⚠ Could not determine video resolution. Using default settings.")
        maxrate = "5000k"
        bufsize = "8000k"
        scale_filter = "scale=1280:720"

    retry_attempts = 0
    while retry_attempts < MAX_RETRIES:
        log_message(f"🎬 Now Streaming: {title} (Attempt {retry_attempts + 1})")

        command = [
            "ffmpeg",
            "-re",
            "-fflags", "+genpts",
            "-rtbufsize", "16M",
            "-probesize", "96M",
            "-analyzeduration", "96M",
            "-reconnect", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "10",
            "-i", url,
            "-i", OVERLAY,
            "-filter_complex",
            f"[0:v] {scale_filter}, [1:v] scale2ref[v0][v1];[v0][v1]overlay=0:0,"
            f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=28:x=20:y=20",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-crf", "18",  # ✅ Better quality for 4K support
            "-maxrate", maxrate,
            "-bufsize", bufsize,
            "-pix_fmt", "yuv420p",
            "-g", "48",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-movflags", "+faststart",
            "-f", "flv",
            RTMP_URL,
            "-loglevel", "warning",
        ]

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            process.wait()

            if process.returncode == 0:
                log_message(f"✅ Streaming '{title}' completed successfully.")
                return

        except Exception as e:
            log_message(f"❌ ERROR: FFmpeg failed for '{title}' - {str(e)}")

        log_message(f"🔄 Retrying '{title}' in 5 seconds...")
        retry_attempts += 1
        time.sleep(5)

    log_message(f"❌ ERROR: '{title}' failed after {MAX_RETRIES} attempts. Skipping movie.")

def main():
    """Main function to stream all movies without interruption."""
    retry_attempts = 0

    while retry_attempts < MAX_RETRIES:
        movies = load_movies()

        if not movies:
            retry_attempts += 1
            log_message(f"❌ ERROR: No movies available! Retrying ({retry_attempts}/{MAX_RETRIES})...")
            time.sleep(60)
            continue

        retry_attempts = 0  # Reset retry counter on success

        while True:
            for movie in movies:
                stream_movie(movie)
                log_message("🔄 Movie ended. Playing next movie...")

            log_message("🔄 All movies played, restarting from the beginning...")

    log_message("❌ ERROR: Maximum retry attempts reached. Exiting.")

if __name__ == "__main__":
    main()
