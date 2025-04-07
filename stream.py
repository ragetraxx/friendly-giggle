import os
import json
import subprocess
import time
import feedparser

# ✅ Configuration
PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")
OVERLAY = os.path.abspath("overlay.png")
RETRY_DELAY = 60
NEWS_FEED_URL = "https://news.google.com/rss"

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

def get_news_ticker():
    """Fetch latest news headlines and return a single ticker string."""
    feed = feedparser.parse(NEWS_FEED_URL)
    headlines = [entry.title for entry in feed.entries[:10]]  # top 10 headlines
    ticker_text = '   ***   '.join(headlines).replace("'", r"\'").replace(":", r"\:").replace('"', r'\"')
    return ticker_text

def load_movies():
    """Load all movies from play.json."""
    try:
        with open(PLAY_FILE, "r") as f:
            movies = json.load(f)
        if not movies:
            print("❌ ERROR: No movies found in play.json!")
            return []
        return movies
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ ERROR: Failed to load {PLAY_FILE} - {str(e)}")
        return []

def stream_movie(movie):
    """Stream a single movie using FFmpeg."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")
    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    news_ticker = get_news_ticker()

    # Text overlays using default system font
    title_text = (
        f"drawtext=text='{title}':"
        f"fontcolor=white:fontsize=20:x=30:y=30"
    )
    ticker_text = (
    f"drawtext=text='{news_ticker}':"
    f"fontcolor=white:fontsize=20:x=w-mod(t*50\,w+tw):y=h-th-10"
    )

    command = [
        "ffmpeg", "-re", "-fflags", "nobuffer", "-i", url, "-i", OVERLAY, "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,{title_text},{ticker_text}",
        "-c:v", "libx264", "-profile:v", "main", "-preset", "veryfast", "-tune", "zerolatency", "-b:v", "2800k",
        "-maxrate", "2800k", "-bufsize", "4000k", "-pix_fmt", "yuv420p", "-g", "50", "-vsync", "cfr",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-f", "flv", "-rtmp_live", "live", RTMP_URL
    ]

    print(f"🎬 Now Streaming: {title}")
    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            print(line, end="")
        process.wait()
    except Exception as e:
        print(f"❌ ERROR: FFmpeg failed for '{title}' - {str(e)}")

def main():
    """Continuously play movies from play.json in a loop."""
    movies = load_movies()
    if not movies:
        print(f"🔄 No movies found! Retrying in {RETRY_DELAY} seconds...")
        time.sleep(RETRY_DELAY)
        return main()

    index = 0
    while True:
        movie = movies[index]
        stream_movie(movie)
        index = (index + 1) % len(movies)
        print("🔄 Movie ended. Playing next movie...")

if __name__ == "__main__":
    main()
