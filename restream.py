import subprocess
import os
import time

RTMP_URL = os.getenv("RTMP_URL")
VIDEO_URL = "https://i3fu7cfu.live.quortex.io/srt_input/1080p_25_fps/hls_target/index.m3u8"
OVERLAY_IMAGE = "live.png"
OVERLAY_TEXT = "LIVE: NATO Summit at The Hague, Netherlands"

def restream(video_url, rtmp_url, overlay_image=None, overlay_text="LIVE"):
    if not rtmp_url:
        raise ValueError("❌ RTMP_URL environment variable not set.")

    overlay_text_escaped = overlay_text.replace(":", r"\\:")

    while True:
        print(f"🎥 Streaming: {video_url} → {rtmp_url}")

        command = [
            "ffmpeg",
            "-fflags", "+genpts+igndts+discardcorrupt",
            "-re",
            "-i", video_url,
        ]

        if overlay_image:
            command += [
                "-loop", "1",
                "-framerate", "1",
                "-i", overlay_image,
                "-filter_complex",
                "[1:v][0:v]scale2ref=w=iw:h=ih[img][vid];"
                "[vid][img]overlay=0:0,"
                f"drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=32:x=35:y=35:box=1:boxcolor=black@0.5"
            ]
        else:
            command += [
                "-vf",
                f"drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=32:x=35:y=35:box=1:boxcolor=black@0.5"
            ]

        command += [
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-b:v", "3000k",
            "-maxrate", "3500k",
            "-bufsize", "1000k",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-g", "50",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-f", "flv",
            rtmp_url
        ]

        try:
            subprocess.run(command)
        except KeyboardInterrupt:
            print("⏹️ Interrupted by user.")
            break
        except Exception as e:
            print(f"❌ FFmpeg error: {e}")

        print("⚠️ Stream stopped. Restarting in 3 seconds...")
        time.sleep(3)

if __name__ == "__main__":
    restream(VIDEO_URL, RTMP_URL, OVERLAY_IMAGE, OVERLAY_TEXT)
