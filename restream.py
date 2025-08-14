import os
import subprocess

# 🔧 Environment variables and config
RTMP_URL = os.getenv("RTMP_URL")
VIDEO_URL = "http://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/stitch/hls/channel/62bdaa32a1b2fd00076693e8/master.m3u8?appName=web&appVersion=unknown&clientTime=0&deviceDNT=0&deviceId=2c7a2d95-35fc-11ef-a031-2b5d494037a2&deviceMake=Chrome&deviceModel=web&deviceType=web&deviceVersion=unknown&includeExtendedEvents=false&serverSideAds=false&sid=53708f79-4a2b-4285-8fa6-e950fc36fb48"
OVERLAY_TEXT = "FBI Files"

# 🔐 Fail if secret not passed correctly
if not RTMP_URL:
    raise ValueError("❌ RTMP_URL is not set. Make sure it's passed via GitHub Secrets or environment.")

# 🔤 Escape colons in drawtext
overlay_text_escaped = OVERLAY_TEXT.replace(":", r"\:")

# 🧪 FFmpeg command
command = [
    "ffmpeg",
    "-fflags", "+genpts+igndts+discardcorrupt",  # Prevent corrupt frame stalls
    "-rw_timeout", "5000000",                    # 5 sec read timeout (input)
    "-timeout", "5000000",                       # 5 sec network timeout
    "-i", VIDEO_URL,                             # HLS input
    "-vf", f"drawtext=text='{overlay_text_escaped}':"
            "fontcolor=white:fontsize=15:x=35:y=35:box=1:boxcolor=black@0.5",
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
