import subprocess
import shlex
import os
import time
import yt_dlp  # You need to install yt-dlp for this

RTMP_URL = os.getenv("RTMP_URL")  # RTMP Server URL
YOUTUBE_URL = "https://www.youtube.com/@rapmafia/live"  # YouTube live URL
OVERLAY_IMAGE = "overlay.png"  # Overlay image (optional)

def get_youtube_stream_url_and_title(youtube_url):
    """Extracts the stream URL and video title from YouTube using yt-dlp."""
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_url, download=False)
            video_url = result['url']
            video_title = result['title']
            print(f"✅ Video URL: {video_url}")
            print(f"✅ Video Title: {video_title}")
            return video_url, video_title
        except yt_dlp.utils.UserNotLive as e:
            print(f"❌ ERROR: The channel is not currently live. Please try again later.")
            return None, None
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return None, None

def restream(video_url, rtmp_url, overlay_image=None, overlay_text="Live: YouTube Video Title"):
    """Continuously re-streams a video to an RTMP server with overlay support."""

    if not rtmp_url or not video_url:
        print("❌ ERROR: RTMP_URL or video URL is not set.")
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

        print(f"FFmpeg command: {' '.join(command)}")  # Log the FFmpeg command
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Capture FFmpeg output
        print("FFmpeg stdout:", process.stdout.decode())
        print("FFmpeg stderr:", process.stderr.decode())

        print("⚠️ Stream stopped. Restarting in 3 seconds...")
        time.sleep(3)  # Shorter restart delay

if __name__ == "__main__":
    # Extract the live stream URL and video title from YouTube
    youtube_stream_url, video_title = get_youtube_stream_url_and_title(YOUTUBE_URL)

    if youtube_stream_url and video_title:
        # Use the title as the overlay text
        overlay_text = f"Live: {video_title}"
        restream(youtube_stream_url, RTMP_URL, OVERLAY_IMAGE, overlay_text)
    else:
        print("❌ ERROR: Could not retrieve video stream details.")
