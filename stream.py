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

# ✅ Sanity Checks
if not RTMP_URL:
    print("❌ ERROR: RTMP_URL is not set!")
    exit(1)

for path, name in [(PLAY_FILE, "Playlist JSON"), (OVERLAY, "Overlay Image"), (FONT_PATH, "Font File")]:
    if not os.path.exists(path):
        print(f"❌ ERROR: {name} '{path}' not found!")
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

def build_ffmpeg_command(url, title):
    text = escape_drawtext(title)

    # Add headers if HLS URL
    input_options = []
    if ".m3u8" in url or "streamsvr" in url:
        print(f"🔐 Spoofing headers for {url}")
        input_options = [
            "-user_agent", "Mozilla/5.0",
            "-headers", "Referer: https://hollymoviehd.cc\r\n"
        ]

    return [
        "ffmpeg",
        "-re",
        "-ss", str(PREBUFFER_SECONDS),
        *input_options,
        "-i", url,
        "-i", OVERLAY,
        "-filter_complex",
        (
            "[0:v]scale=1280:720:flags=bicubic[v];"
            "[1:v]scale=1280:720[ol];"
            "[v][ol]overlay=0:0[vo];"
            "[vo]drawtext=fontfile='{font}':text='{text}':fontcolor=white:fontsize=18:x=30:y=30"
        ).format(font=FONT_PATH, text=text),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "zerolatency",
        "-g", "60",
        "-keyint_min", "60",
        "-sc_threshold", "0",
        "-b:v", "3000k",
        "-maxrate", "5000k",
        "-bufsize", "5000k",
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
        print(f"❌ Skipping '{title}': no URL")
        return

    print(f"🎬 Streaming: {title}")
    command = build_ffmpeg_command(url, title)

    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            if "403 Forbidden" in line:
                print(f"🚫 403 Forbidden! Skipping: {title}")
                process.kill()
                return
            print(line.strip())
        process.wait()
    except Exception as e:
        print(f"❌ FFmpeg crashed: {e}")

def main():
    movies = load_movies()
    if not movies:
        print(f"📂 No entries in {PLAY_FILE}. Retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
        return main()

    index = 0
    while True:
        stream_movie(movies[index])
        index = (index + 1) % len(movies)
        print("⏭️  Next movie in 5s...")
        time.sleep(5)

if __name__ == "__main__":
    main()
