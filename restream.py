import subprocess
import shlex
import os
import time

RTMP_URL = os.getenv("RTMP_URL")  # RTMP Server URL
VIDEO_URL = "http://fl6.moveonjoy.com/NBA_10/index.m3u8"  # Video source
OVERLAY_IMAGE = "overlay.png"  # Overlay image (optional)
OVERLAY_TEXT = "NBA Live"  # Overlay text

def restream(video_url, rtmp_url, overlay_image=None, overlay_text="NBA Live"):
    """Continuously re-streams a video to an RTMP server with overlay support."""

    if not rtmp_url:
        print("❌ ERROR: RTMP_URL is not set.")
        return

    while True:  # Infinite loop to restart FFmpeg if it stops
        print(f"🎥 Streaming: {video_url} → {rtmp_url}")

        video_url_escaped = shlex.quote(video_url)
        overlay_text_escaped = overlay_text.replace(":", r"\:")  # Escape colon properly

        command = [
            "ffmpeg",
            "-re",
            "-i", video_url_escaped,  # Input video source
        ]

        # Check if an overlay image is provided
        if overlay_image:
            overlay_path_escaped = shlex.quote(overlay_image)
            command += [
                "-i", overlay_path_escaped,  # Input overlay image
                "-filter_complex",
                "[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=10:10,"
                "drawbox=x=10:y=10:w=200:h=40:color=blue@0.7:t=fill,"
                f"drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=20:x=20:y=20"
            ]
        else:
            command += [
                "-vf",
                f"drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=24:x=15:y=15"
            ]

        # Video encoding settings
        command += [
            "-c:v", "libx264",
            "-preset", "slow",
            "-tune", "zerolatency",
            "-b:v", "6000k",
            "-maxrate", "7000k",
            "-bufsize", "2000k",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-g", "25",
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
    restream(VIDEO_URL, RTMP_URL, OVERLAY_IMAGE, OVERLAY_TEXT)
