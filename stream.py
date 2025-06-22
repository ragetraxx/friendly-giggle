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
NEXT_DELAY = 5
PREBUFFER_SECONDS = 5

# ✅ Sanity Checks
if not RTMP_URL:
    print("❌ ERROR: RTMP_URL is not set!")
    exit(1)

for path, label in [(PLAY_FILE, "Playlist"), (OVERLAY, "Overlay"), (FONT_PATH, "Font")]:
    if not os.path.exists(path):
        print(f"❌ {label} '{path}' not found!")
        exit(1)

def load_movies():
    try:
        with open(PLAY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load play.json: {e}")
        return []

def escape_drawtext(text):
    return text.replace('\\', '\\\\\\\\').replace(':', '\\:').replace("'", "\\'")

def build_ffmpeg_command(url, title):
    text = escape_drawtext(title)

    headers = []
    if "streamsvr" in url or "pkaystream" in url:
        print("📡 Spoofing headers for streamsvr...")
        headers = [
            "-user_agent", "Mozilla/5.0",
            "-headers", "Referer: https://pkaystream.cc\r\n"
        ]

    return [
        "ffmpeg",
        "-ss", str(PREBUFFER_SECONDS),  # ⏪ Prebuffer before sending to RTMP
        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "2",
        "-probesize", "10000000",
        "-analyzeduration", "10000000",
        *headers,
        "-i", url,
        "-i", OVERLAY,
        "-filter_complex",
        f"[0:v]scale=960:540:flags=bicubic,unsharp=5:5:0.8:5:5:0.0[v];"
        f"[1:v]scale=960:540[ol];"
        f"[v][ol]overlay=0:0[vo];"
        f"[vo]drawtext=fontfile='{FONT_PATH}':text='{text}':fontcolor=white:fontsize=13:x=30:y=30",
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-g", "60",
        "-keyint_min", "60",
        "-sc_threshold", "0",
        "-b:v", "1500k",
        "-maxrate", "1500k",
        "-bufsize", "3000k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        "-f", "flv",
        RTMP_URL
    ]

def stream_movie(movie):
    title = movie.get("title", "Untitled")
    url = movie.get("url")

    if not url:
        print(f"⚠️  Skipping '{title}' - no URL")
        return

    print(f"🎬 Streaming: {title}")
    cmd = build_ffmpeg_command(url, title)

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            if "403" in line:
                print(f"🚫 403 Forbidden! Skipping: {title}")
                process.kill()
                time.sleep(2)
                return
            if "error" in line.lower() or "failed" in line.lower():
                print("⚠️ ", line.strip())
            else:
                print(line.strip())
        process.wait()
    except Exception as e:
        print(f"❌ Crash: {e}")
        time.sleep(2)

def main():
    movies = load_movies()
    if not movies:
        print(f"📂 Empty playlist. Retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
        return main()

    index = 0
    while True:
        stream_movie(movies[index])
        index = (index + 1) % len(movies)
        print(f"⏭️  Next in {NEXT_DELAY}s...")
        time.sleep(NEXT_DELAY)

if __name__ == "__main__":
    main()
