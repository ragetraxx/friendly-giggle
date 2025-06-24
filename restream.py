import subprocess
import os
import time

# ✅ Get RTMP URL from GitHub Actions secret environment variable
RTMP_URL = os.getenv("RTMP_URL")
VIDEO_URL = "https://i3fu7cfu.live.quortex.io/srt_input/1080p_25_fps/hls_target/index.m3u8"
OVERLAY_IMAGE = "live.png"
OVERLAY_TEXT = "LIVE: NATO Summit at The Hague, Netherlands"

def restream(video_url, rtmp_url, overlay_image=None, overlay_text="LIVE"):
    if not rtmp_url:
        print("❌ ERROR: RTMP_URL is not set.")
        return

    while True:
        print(f"🎥 Streaming: {video_url} → {rtmp_url}")

        overlay_text_escaped = overlay_text.replace(":", r"\\:")

        command = [
            "ffmpeg",
            "-re",
            "-i", video_url,
        ]

        if overlay_image:
            command += [
                "-loop", "1",
                "-framerate", "1",
                "-i", overlay_image,
                "-filter_complex",
                f"[0:v][1:v]overlay=10:10,drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=20:x=30:y=30"
            ]
        else:
            command += [
                "-vf",
                f"drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=20:x=30:y=30"
            ]

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

        try:
            subprocess.run(command)
        except KeyboardInterrupt:
            print("⏹️ Interrupted.")
            break
        except Exception as e:
            print(f"❌ FFmpeg error: {e}")

        print("⚠️ Stream stopped. Restarting in 3 seconds...")
        time.sleep(3)

if __name__ == "__main__":
    restream(VIDEO_URL, RTMP_URL, OVERLAY_IMAGE, OVERLAY_TEXT)
