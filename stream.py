import os
import json
import subprocess
import time
import feedparser

# ✅ Configuration
PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")
OVERLAY = os.path.abspath("overlay.png")
NEWS_URL = "https://news.google.com/rss"
RETRY_DELAY = 60

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

def fetch_news():
    """Fetch all news headlines from RSS feed once per workflow run."""
    try:
        feed = feedparser.parse(NEWS_URL)
        headlines = [entry.title for entry in feed.entries]
        return " | ".join(headlines)  # Concatenate all headlines for scrolling effect
    except Exception as e:
        print(f"❌ ERROR: Failed to fetch news - {e}")
        return "Latest news unavailable"

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

def stream_movie(movie, news_text):
    """Stream a single movie using FFmpeg with a scrolling news ticker."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')
    news_text = news_text.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg", "-re", "-fflags", "nobuffer", "-i", url, "-i", OVERLAY, "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=20:x=30:y=30,drawtext=text='{news_text}':fontcolor=yellow:fontsize=18:x=w-10*t:y=h-40",
        "-c:v", "libx264", "-profile:v", "main", "-preset", "veryfast", "-tune", "zerolatency", "-b:v", "2800k",
        "-maxrate", "2800k", "-bufsize", "4000k", "-pix_fmt", "yuv420p", "-g", "50", "-vsync", "cfr",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-f", "flv", "-rtmp_live", "live", RTMP_URL
    ]

    print(f"🎬 Now Streaming: {title}")

    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        process.wait()
    except Exception as e:
        print(f"❌ ERROR: FFmpeg failed for '{title}' - {str(e)}")

def main():
    """Continuously play movies from play.json in a loop with a scrolling news ticker that updates only on workflow runs."""
    movies = load_movies()
    
    if not movies:
        print(f"🔄 No movies found! Retrying in {RETRY_DELAY} seconds...")
        time.sleep(RETRY_DELAY)
        return main()

    index = 0  # Track current movie index
    news_text = fetch_news()  # Fetch news once per workflow run

    while True:
        movie = movies[index]
        stream_movie(movie, news_text)

        # Move to the next movie, looping back if at the end
        index = (index + 1) % len(movies)
        print("🔄 Movie ended. Playing next movie...")

if __name__ == "__main__":
    main()
