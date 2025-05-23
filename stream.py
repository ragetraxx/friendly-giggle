import os
import json
import subprocess
import time

# ✅ Configuration
PLAY_FILE = "play.json"
RTMP_URL = os.getenv("RTMP_URL")
OVERLAY = os.path.abspath("overlay.png")
FONT_PATH = os.path.abspath("Roboto-Black.ttf")
RETRY_DELAY = 60
PREBUFFER_SECONDS = 10
MAXRATE_KBPS = 2500  # Fixed maxrate for SD Wi-Fi streaming

# ✅ Sanity Checks
if not RTMP_URL:
    print("❌ ERROR: RTMP_URL is not set!")
    exit(1)

if not os.path.exists(PLAY_FILE):
    print(f"❌ ERROR: {PLAY_FILE} not found!")
    exit(1)

if not os.path.exists(OVERLAY):
    print(f"❌ ERROR: Overlay image '{OVERLAY}' not found!")
    exit(1)

if not os.path.exists(FONT_PATH):
    print(f"❌ ERROR: Font file '{FONT_PATH}' not found!")
    exit(1)

def load_movies():
    try:
        with open(PLAY_FILE, "r") as f:
            return json.load(f) or []
    except Exception as e:
        print(f"❌ Failed to load {PLAY_FILE}: {e}")
        return []

def escape_drawtext(text):
    return text.replace('\\', '\\\\\\\\').replace(':', '\\:').replace("'", "\\'")

def stream_movie(movie):
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")
    if not url:
        print(f"❌ Missing URL for '{title}'")
        return

    if url.startswith("http"):
        print(f"⚠️ Streaming from remote URL: {url} — may cause buffering.")

    text = escape_drawtext(title)

    command = [
        "ffmpeg",
        "-ss", f"{PREBUFFER_SECONDS}",
        "-fflags", "+nobuffer+genpts+discardcorrupt",
        "-flags", "low_delay",
        "-avioflags", "direct",
        "-probesize", "100M",
        "-analyzeduration", "20M",
        "-rw_timeout", "10000000",
        "-timeout", "10000000",
        "-thread_queue_size", "1024",
        "-i", url,
        "-i", OVERLAY,
        "-filter_complex",
        (
            "[0:v]scale=w=720:h=480:force_original_aspect_ratio=decrease:flags=bicubic,"
            "pad=w=720:h=480:x=(ow-iw)/2:y=(oh-ih)/2:color=black[v];"
            "[1:v]scale=720:480[ol];"
            "[v][ol]overlay=0:0[vo];"
            "[vo]drawtext=fontfile='{font}':text='{text}':fontcolor=white:fontsize=16:x=30:y=30"
        ).format(font=FONT_PATH, text=text),
        "-c:v", "libx264",
        "-preset", "fast",
        "-tune", "zerolatency",
        "-g", "60",
        "-keyint_min", "60",
        "-sc_threshold", "0",
        "-maxrate", f"{MAXRATE_KBPS}k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-flush_packets", "1",
        "-f", "flv",
        RTMP_URL
    ]

    print(f"🎬 Streaming: {title} (720x480, maxrate: {MAXRATE_KBPS}k)")
    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            print(line, end="")
        process.wait()
    except Exception as e:
        print(f"❌ FFmpeg error: {e}")

def main():
    movies = load_movies()
    if not movies:
        print(f"🔁 No movies. Retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
        return main()

    index = 0
    while True:
        stream_movie(movies[index])
        index = (index + 1) % len(movies)
        print("⏳ Waiting 5s before next movie...")
        time.sleep(5)

if __name__ == "__main__":
    main()
