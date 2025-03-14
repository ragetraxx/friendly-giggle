import subprocess
import shlex

# Configuration
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"  # RTMP Server URL
VIDEO_URL = "https://rtmp-live-ingest-prod.euwest1.akamaized.net/transmuxv1/streams/a1d5f9c9-d178-c00c-84ff-1cc337f7cf91.m3u8"  # Your video/audio source
OVERLAY_IMAGE = None  # Optional overlay image
OVERLAY_TEXT = "LIVE: The Hague, Netherlands"  # Text overlay on the video

def restream(video_url, rtmp_url, overlay_image=None, overlay_text="LIVE: The Hague, Netherlands"):
    """Re-streams a video or audio stream to an RTMP server with overlay text/image."""
    
    video_url_escaped = shlex.quote(video_url)
    overlay_text_escaped = overlay_text.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg",
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-strict", "experimental",
        "-probesize", "32M",
        "-analyzeduration", "0",
        "-i", video_url_escaped,  # Input video/audio source
    ]

    # Check if overlay image is provided
    if overlay_image:
        overlay_path_escaped = shlex.quote(overlay_image)
        command += [
            "-i", overlay_path_escaped,
            "-filter_complex",
            f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=10:10,"
            f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=30:x=30:y=30:box=1:boxcolor=black@0.5:boxborderw=5"
        ]
    else:
        command += [
            "-vf",
            f"drawtext=text='{overlay_text_escaped}':fontcolor=white:fontsize=30:x=20:y=20:box=1:boxcolor=black@0.5:boxborderw=5"
        ]

    # Optimize Video Quality & Reduce Blur
    command += [
        "-c:v", "libx264",
        "-preset", "superfast",  # Fast encoding with better quality than "ultrafast"
        "-tune", "film",  # Enhances clarity, reduces blur
        "-b:v", "5000k",  # Higher video bitrate for better quality
        "-maxrate", "6000k",
        "-bufsize", "12000k",
        "-g", "30",  # Reduce keyframe interval for lower latency
        "-pix_fmt", "yuv420p",  # Ensures compatibility with most devices
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-af", "aresample=async=1:min_hard_comp=0.100000:first_pts=0",  # Fix audio desync issues
        "-rtbufsize", "100M",
        "-vsync", "1",
        "-preset", "superfast",
        "-tune", "zerolatency",
        "-f", "flv",
        rtmp_url
    ]

    print(f"🎬 Now Restreaming: {video_url} with overlay text: {overlay_text}")
    subprocess.run(command)

if __name__ == "__main__":
    restream(VIDEO_URL, RTMP_URL, OVERLAY_IMAGE, OVERLAY_TEXT)
