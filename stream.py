import json
import datetime
import time
import shlex
import subprocess

# 🔹 RTMP Streaming URL
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
# 🔹 Overlay Image (PNG with transparency)
OVERLAY = "overlay.png"

# 🔹 Load schedule
def load_schedule():
    with open("now_showing.json", "r") as file:
        return json.load(file)

# 🔹 Find the movie that should be playing right now
def get_current_movie():
    schedule = load_schedule()
    now = datetime.datetime.utcnow()

    for movie in schedule:
        start_time = datetime.datetime.strptime(movie["start_time"], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(movie["end_time"], "%Y-%m-%d %H:%M:%S")

        if start_time <= now < end_time:
            elapsed_time = (now - start_time).seconds  # 🔹 How many seconds into the movie we are
            return movie, elapsed_time

    return None, 0  # No movie is currently scheduled

# 🔹 Stream movie at the correct timestamp
def stream_movie(movie, elapsed_time):
    url = movie["url"]
    title = movie["title"]

    # 🔹 Escape special characters
    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
    overlay_text = shlex.quote(title)
    
    # 🔹 Fix colon issue
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg",
        "-re",
        "-fflags", "+genpts",
        "-rtbufsize", "128M",
        "-probesize", "10M",
        "-analyzeduration", "1000000",
        "-ss", str(elapsed_time),  # 🔹 Start at the correct timestamp
        "-i", video_url_escaped,
        "-i", overlay_path_escaped,
        "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,"
        f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-b:v", "2500k",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-pix_fmt", "yuv420p",
        "-g", "50",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-f", "flv",
        RTMP_URL
    ]

    print(f"🎬 Now Streaming: {title} (Starting from {elapsed_time} seconds)")
    subprocess.run(command)

# 🔹 Continuous streaming loop
while True:
    current_movie, elapsed_time = get_current_movie()

    if current_movie:
        stream_movie(current_movie, elapsed_time)
    else:
        print("⚠️ No movie is currently scheduled! Waiting...")
        time.sleep(60)  # 🔹 Check again in 1 minute
