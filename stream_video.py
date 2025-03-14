import subprocess
import shlex

# Configuration
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"  # RTMP Server URL
VIDEO_URL = "https://rtmp-live-ingest-eu-west-3-universe-dacast-com.akamaized.net/transmuxv1/streams/a1d5f9c9-d178-c00c-84ff-1cc337f7cf91.m3u8"  # Your video/audio source
OVERLAY_IMAGE = "overlay.png"  # Your overlay image (leave blank if not needed)
OVERLAY_TEXT = "LIVE: The Hague, Netherlands"  # Text overlay on the video

def restream(video_url, rtmp_url, overlay_image=None, overlay_text="LIVE: The Hague, Netherlands"):
    """Re-streams a video or audio stream to an RTMP server with an optional overlay."""
    
    video_url_escaped = shlex.quote(video_url)
    overlay_text_escaped = overlay_text.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

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
            f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,"
            f"drawbox=x=10:y=10:w=400:h=40:color=blue@0.7:t=fill,"
            f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20"
        ]
    else:
        command += [
            "-vf",
            f"drawbox=x=10:y=10:w=400:h=40:color=blue@0.7:t=fill,"
            f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20"
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
