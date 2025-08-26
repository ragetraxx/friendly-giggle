#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
import signal
from pathlib import Path

# ---------- CONFIG ----------
RTMP_URL = os.getenv("RTMP_URL")
VIDEO_URL = "https://utube.antang-rage.workers.dev/@HouseofRepresentativesPH/stream.m3u8"
LOGO_FILE = "live.png"   # ensure this file exists in the working directory (or give full path)
# ----------------------------

if not RTMP_URL:
    print("❌ RTMP_URL not found in environment. Set it via GitHub Secrets.", file=sys.stderr)
    sys.exit(2)

if not shutil.which("ffmpeg"):
    print("❌ ffmpeg not found in PATH.", file=sys.stderr)
    sys.exit(2)

logo_path = Path(LOGO_FILE)
use_overlay = logo_path.exists()

# Build ffmpeg command. Using list form avoids shell interpretation of '@' or other chars.
# We include reconnect options and -nostdin for CI friendliness.
command = [
    "ffmpeg",
    "-nostdin",
    "-fflags", "+genpts+igndts+discardcorrupt",
    "-rw_timeout", "5000000",
    "-timeout", "5000000",
    # reconnect options placed before -i to help with flaky HLS sources
    "-reconnect", "1", "-reconnect_at_eof", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "2",
    "-i", VIDEO_URL,
]

if use_overlay:
    # second input is the overlay image
    command += ["-i", str(logo_path)]
    # scale the image to the video's resolution and overlay at 0,0 (full-screen)
    filter_complex = "[1:v][0:v]scale2ref=w=iw:h=ih[overlay][base];[base][overlay]overlay=0:0:format=auto"
    command += ["-filter_complex", filter_complex]
else:
    # no overlay; passthrough video
    pass

# video + audio encoding / streaming options
command += [
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

print("🔁 Starting restream")
print("  input:", VIDEO_URL)
print("  rtmp:", RTMP_URL)
print("  overlay:", "enabled" if use_overlay else "disabled")
print("  ffmpeg:", shutil.which("ffmpeg"))

# Start FFmpeg
proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

# handle graceful shutdown in runners / ctrl+c
def terminate(child_proc):
    try:
        if child_proc and child_proc.poll() is None:
            print("🛑 Terminating ffmpeg...", file=sys.stderr)
            child_proc.terminate()
            child_proc.wait(timeout=10)
    except Exception:
        try:
            child_proc.kill()
        except Exception:
            pass

def sigterm_handler(signum, frame):
    terminate(proc)
    sys.exit(0)

signal.signal(signal.SIGINT, sigterm_handler)
signal.signal(signal.SIGTERM, sigterm_handler)

# Stream ffmpeg stdout to console in real time
try:
    for line in proc.stdout:
        # print line as-is so GitHub Actions logs show ffmpeg progress/errors
        print(line, end="")
    retcode = proc.wait()
    print(f"ffmpeg exited with code {retcode}")
    sys.exit(retcode if retcode is not None else 0)
except Exception as e:
    print("Exception while running ffmpeg:", e, file=sys.stderr)
    terminate(proc)
    sys.exit(1)
