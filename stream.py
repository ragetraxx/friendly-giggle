import json
import random
import time
import subprocess
import shlex
import datetime

MOVIE_FILE = "movies.json"
EPG_FILE = "epg.xml"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"
EPG_DURATION_HOURS = 6

def load_movies():
    """Load movies from JSON file."""
    with open(MOVIE_FILE, "r") as f:
        return json.load(f)

def generate_epg(movies):
    """Generate a new EPG XML file for the next 6 hours."""
    start_time = datetime.datetime.utcnow()
    epg_data = """<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n"""
    
    for i in range(EPG_DURATION_HOURS * 2):  # Assuming average movie length is ~3 hours
        movie = random.choice(movies)
        start_str = start_time.strftime("%Y%m%d%H%M%S") + " +0000"
        end_time = start_time + datetime.timedelta(hours=3)  # Adjust based on movie length
        end_str = end_time.strftime("%Y%m%d%H%M%S") + " +0000"

        epg_data += f"""    <programme start="{start_str}" stop="{end_str}" channel="bihm">
        <title>{movie["title"]}</title>
        <desc>{movie.get("description", "No description available")}</desc>
    </programme>\n"""

        start_time = end_time  # Move to the next time slot

    epg_data += "</tv>"

    with open(EPG_FILE, "w") as f:
        f.write(epg_data)
    print("Generated new EPG.")

def stream_movie(movie):
    """Stream a movie to the RTMP server."""
    title = movie["title"]
    url = movie["url"]

    # Escape paths to prevent issues
    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
    overlay_text = shlex.quote(title)

    command = f"""
    ffmpeg -re -fflags nobuffer -rtbufsize 128M -probesize 10M -analyzeduration 1000000 \
    -threads 2 -i {video_url_escaped} -i {overlay_path_escaped} \
    -filter_complex "[1:v]scale2ref=w=main_w:h=main_h:force_original_aspect_ratio=decrease[ovr][base];[base][ovr]overlay=0:0,drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20,fps=30" \
    -c:v libx264 -preset fast -tune zerolatency -b:v 2500k -maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 50 \
    -c:a aac -b:a 192k -ar 48000 -f flv {shlex.quote(RTMP_URL)}
    """

    subprocess.run(command, shell=True)

def main():
    """Main function to control movie streaming and EPG generation."""
    while True:
        movies = load_movies()
        generate_epg(movies)  # Generate a new EPG every cycle

        start_time = time.time()
        while time.time() - start_time < EPG_DURATION_HOURS * 3600:
            for movie in movies:
                print(f"Streaming: {movie['title']}")
                stream_movie(movie)

if __name__ == "__main__":
    main()