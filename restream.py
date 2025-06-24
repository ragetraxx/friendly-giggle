import os
import subprocess

RTMP_URL = os.getenv("RTMP_URL")
VIDEO_URL = "https://i3fu7cfu.live.quortex.io/srt_input/1080p_25_fps/hls_target/index.m3u8"

if not RTMP_URL:
    raise ValueError("❌ RTMP_URL not set")

command = [
    "ffmpeg",
    "-re",
    "-i", VIDEO_URL,
    "-vf", "drawtext=text='LIVE TEST':fontcolor=white:fontsize=30:x=10:y=10:box=1:boxcolor=black@0.5",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-b:v", "2500k",
    "-maxrate", "3000k",
    "-bufsize", "1000k",
    "-c:a", "aac",
    "-ar", "44100",
    "-b:a", "128k",
    "-f", "flv",
    RTMP_URL
]

print(f"Streaming to: {RTMP_URL}")
subprocess.run(command)
