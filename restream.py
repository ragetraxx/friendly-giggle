import os
import subprocess
import sys
import signal

RTMP_URL = os.getenv("RTMP_URL")
VIDEO_URL = "http://103.236.179.86:80/live/rictms/rictms/5442.m3u8"
LOGO_FILE = "live.png"

if not RTMP_URL:
    print("❌ RTMP_URL not found in environment", file=sys.stderr)
    sys.exit(1)

command = [
    "ffmpeg",
    "-nostdin",
    "-fflags", "+genpts+igndts+discardcorrupt",
    "-rw_timeout", "5000000",
    "-timeout", "5000000",
    "-reconnect", "1",
    "-reconnect_at_eof", "1",
    "-reconnect_streamed", "1",
    "-reconnect_delay_max", "10",
    "-i", VIDEO_URL,
    "-i", LOGO_FILE,
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

print("🚀 Starting stream...")
proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Graceful shutdown
def handle_stop(signum, frame):
    print("🛑 Signal received, stopping FFmpeg...")
    if proc.poll() is None:  # Still running
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_stop)
signal.signal(signal.SIGTERM, handle_stop)

# Stream logs safely
try:
    for line in proc.stdout:
        print(line, end="")
except Exception as e:
    print(f"⚠ Error reading output: {e}", file=sys.stderr)

proc.wait()
print(f"FFmpeg exited with code {proc.returncode}")
