import os
import subprocess

# 🔧 Environment variables and config
RTMP_URL = os.getenv("RTMP_URL")
VIDEO_URL = "https://utube.antang-rage.workers.dev/@HouseofRepresentativesPH/stream.m3u8"
LOGO_FILE = "live.png"  # Path to your overlay image

# 🔐 Fail if secret not passed correctly
if not RTMP_URL:
    raise ValueError("❌ RTMP_URL is not set. Make sure it's passed via GitHub Secrets or environment.")

# 🧪 FFmpeg command
command = [
    "ffmpeg",
    "-fflags", "+genpts+igndts+discardcorrupt",
    "-rw_timeout", "5000000",
    "-timeout", "5000000",
    "-i", VIDEO_URL,   # Video input
    "-i", LOGO_FILE,   # Overlay image input
    "-filter_complex",
    "[1:v][0:v]scale2ref=w=iw:h=ih[overlay][base];[base][overlay]overlay=0:0:format=auto",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-b:v", "2500k",
    "-maxrate", "2800k",
    "-bufsize", "1000k",
    "-g", "50",
    "-keyint_min", "25",
    "-x264opts", "keyint=50:min-keyint=25:no-scenecut",
    "-c:a", "aac",
    "-b:a", "128k",
    "-ar", "44100",
    "-f", "flv",
    RTMP_URL
]

# ▶️ Run the command and stream
print(f"📡 Streaming to: {RTMP_URL}")
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
print(result.stdout)
