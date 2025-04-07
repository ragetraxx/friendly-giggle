import os
import json
import subprocess
import time
import feedparser

# ✅ Configuration
PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")
OVERLAY = os.path.abspath("overlay.png")
NEWS_FEED = "https://news.google.com/rss"
TICKER_UPDATE_INTERVAL = 300  # Update news every 5 minutes
RETRY_DELAY = 60

def fetch_latest_news():
    """Fetch latest headlines from Google News RSS feed."""
    feed = feedparser.parse(NEWS_FEED)
    headlines = [entry.title for entry in feed.entries[:5]]  # Get top 5 headlines
    return "  |  ".join(headlines) if headlines else "No latest news available."

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
    """Stream a single movie with an overlay and news ticker."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')
    news_text = news_text.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg", "-re", "-fflags", "nobuffer", "-i", url, "-i", OVERLAY, "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=20:x=30:y=30,
        drawtext=text='{news_text}':fontcolor=yellow:fontsize=18:x=(w-text_w-30):y=(h-50):enable='mod(t,10)'",
        "-c:v", "libx264", "-profile:v", "main", "-preset", "veryfast", "-tune", "zerolatency", "-b:v", "2800k",
        "-maxrate", "2800k", "-bufsize", "4000k", "-pix_fmt", "yuv420p", "-g", "50", "-vsync", "cfr",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-f", "flv", "-rtmp_live", "live", RTMP_URL
    ]

    print(f"🎬 Now Streaming: {title}")

    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            print(line, end="")  # Optional: Log errors in real-time
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
    
    index = 0  # Track current movie index
    last_news_update = 0
    news_text = fetch_latest_news()

    while True:
        if time.time() - last_news_update > TICKER_UPDATE_INTERVAL:
            news_text = fetch_latest_news()
            last_news_update = time.time()
            print("📰 News ticker updated.")
        
        movie = movies[index]
        stream_movie(movie, news_text)
        
        index = (index + 1) % len(movies)
        print("🔄 Movie ended. Playing next movie...")

if __name__ == "__main__":
    main()
