import os
import subprocess

# 🔧 Environment variables and config
RTMP_URL = os.getenv("RTMP_URL")
VIDEO_URL = "https://stitcher-ipv4.pluto.tv/v1/stitch/embed/hls/channel/6792c30abc03978b9b8bb832/master.m3u8?deviceType=samsung-tvplus&deviceMake=samsung&deviceModel=samsung&deviceVersion=unknown&appVersion=unknown&deviceLat=0&deviceLon=0&deviceDNT=%7BTARGETOPT%7D&deviceId=%7BPSID%7D&advertisingId=%7BPSID%7D&us_privacy=1YNY&samsung_app_domain=%7BAPP_DOMAIN%7D&samsung_app_name=%7BAPP_NAME%7D&profileLimit=&profileFloor=&embedPartner=samsung-tvplus"
OVERLAY_TEXT = "NBA"

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
