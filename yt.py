import os
import subprocess
import shlex
import time
import yt_dlp

RTMP_URL = os.getenv("RTMP_URL")  # RTMP server URL from GitHub Secrets
YOUTUBE_URL = "https://www.youtube.com/@rapmafia/live"
OVERLAY = "overlay.png"  # Ensure this file exists in the working directory

def get_youtube_stream_url_and_title(youtube_url):
    """Extracts the live video stream URL and title from a YouTube channel."""
    ydl_opts = {
        'quiet': True,
        'force_generic_extractor': False,
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_url, download=False)
            if 'url' in result:
                return result['url'], result['title']
            else:
                raise Exception("No live stream found.")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None, None

def restream(url, title):
    """Streams YouTube live to RTMP with an overlay."""
    if not url or not RTMP_URL:
        print("❌ ERROR: Missing stream URL or RTMP URL.")
        return
    
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')
    
    command = [
        "ffmpeg", "-re", "-fflags", "nobuffer", "-i", url, "-i", OVERLAY, "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=20:x=30:y=30",
        "-c:v", "libx264", "-profile:v", "main", "-preset", "veryfast", "-tune", "zerolatency", "-b:v", "2800k",
        "-maxrate", "2800k", "-bufsize", "4000k", "-pix_fmt", "yuv420p", "-g", "50", "-vsync", "cfr",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-f", "flv", "-rtmp_live", "live", RTMP_URL
    ]
    
    print(f"🎥 Streaming: {url} → {RTMP_URL}")
    
    while True:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in process.stderr:
            print(line, end="")  # Log FFmpeg errors in real-time
        
        print("⚠️ Stream stopped. Restarting in 3 seconds...")
        time.sleep(3)  # Short delay before retrying

if __name__ == "__main__":
    youtube_stream_url, video_title = get_youtube_stream_url_and_title(YOUTUBE_URL)
    if youtube_stream_url:
        restream(youtube_stream_url, video_title)
    else:
        print("❌ No live stream available. Exiting...")
