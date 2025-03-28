import subprocess
import shlex
import os

# Load RTMP URL from environment variable (GitHub Secret)
RTMP_URL = os.getenv("RTMP_URL")  # RTMP Server URL (stored as a GitHub Secret)
VIDEO_URL = "http://fl6.moveonjoy.com/NBA_11/index.m3u8"  # Video/audio source
OVERLAY_IMAGE = "overlay.png"  # Overlay image (leave blank if not needed)
OVERLAY_TEXT = "NBA Live"  # Text overlay on the video

def restream(video_url, rtmp_url, overlay_image=None, overlay_text="NBA Live"):
    """Re-streams a video or audio stream to an RTMP server with an optional overlay."""
    
    if not rtmp_url:
        print("❌ ERROR: RTMP_URL is not set. Please check your environment variables.")
        return
    
    video_url_escaped = shlex.quote(video_url)
    overlay_text_escaped = overlay_text.replace(":", r"\:")  # Escape colon properly

    command = [
        "ffmpeg",
        "-re",
        "-i", video_url_escaped,  # Input video or audio stream
    ]
    
    # Check if an overlay image is provided
    if overlay_image:
        overlay_path_escaped = shlex.quote(overlay_image)
        command += [
            "-i", overlay_path_escaped,
            "-filter_complex",
            f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0," \
            f"drawbox=x=10:y=10:w=text_w+20:h=30:color=blue@0.7:t=fill," \
            f"drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=20:x=15:y=15"
        ]
    else:
        command += [
            "-vf",
            f"drawbox=x=10:y=10:w=text_w+20:h=30:color=blue@0.7:t=fill," \
            f"drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=20:x=15:y=15"
        ]
    
    # Video encoding settings
    command += [
        "-c:v", "libx264",
        "-preset", "fast",
        "-tune", "film",
        "-b:v", "4000k",
        "-crf", "23",
        "-maxrate", "4500k",
        "-bufsize", "6000k",
        "-pix_fmt", "yuv420p",
        "-g", "50",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-f", "flv",
        rtmp_url
    ]

    print(f"🎥 Now Restreaming: {video_url}")
    subprocess.run(command)

if __name__ == "__main__":
    restream(VIDEO_URL, RTMP_URL, OVERLAY_IMAGE, OVERLAY_TEXT)
