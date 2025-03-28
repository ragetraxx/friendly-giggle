import subprocess
import shlex
import os
import time

RTMP_URL = os.getenv("RTMP_URL")  # RTMP Server URL
VIDEO_URL = "http://fl6.moveonjoy.com/NBA_3/index.m3u8"  # Video source
OVERLAY_IMAGE = "overlay.png"  # Overlay image (optional)
OVERLAY_TEXT = "NBA Live"  # Overlay text

def restream(video_url, rtmp_url, overlay_text="NBA Live"):
    """Continuously re-streams a video to an RTMP server with optimized settings."""

    if not rtmp_url:
        print("❌ ERROR: RTMP_URL is not set.")
        return

    while True:  # Infinite loop to restart FFmpeg if it stops
        print(f"🎥 Streaming: {video_url} → {rtmp_url}")

        command = [
            "ffmpeg",
            "-re",
            "-i", video_url,
            "-vf",
            f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=15:y=15",
            "-c:v", "libx264",
            "-preset", "slow",  # Change to "ultrafast" for low-latency streaming
            "-tune", "zerolatency",
            "-b:v", "6000k",  # Increase bitrate for higher quality
            "-maxrate", "7000k",
            "-bufsize", "2000k",  # Lower buffer size to reduce latency
            "-crf", "18",  # Higher quality (lower values = better quality)
            "-pix_fmt", "yuv420p",
            "-g", "25",  # Lower GOP for faster frame updates
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-f", "flv",
            rtmp_url
        ]

        process = subprocess.run(command)

        print("⚠️ Stream stopped. Restarting in 3 seconds...")
        time.sleep(3)  # Shorter restart delay

if __name__ == "__main__":
    restream(VIDEO_URL, RTMP_URL)
