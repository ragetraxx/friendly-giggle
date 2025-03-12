import json
import random
import time
import subprocess
import shlex
import datetime
import os

MOVIE_FILE = "movies.json"
EPG_FILE = "epg.xml"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"
EPG_DURATION_HOURS = 6

def load_movies():
    """Load movies from JSON file."""
    if not os.path.exists(MOVIE_FILE):
        print(f"❌ ERROR: {MOVIE_FILE} not found!")
        return []

    with open(MOVIE_FILE, "r") as f:
        try:
            movies = json.load(f)
            if not movies:
                print("❌ ERROR: movies.json is empty!")
            return movies
        except json.JSONDecodeError:
            print("❌ ERROR: Failed to parse movies.json!")
            return []

def generate_epg(movies):
    """Generate a new EPG XML file for the next 6 hours with random movies."""
    if not movies:
        print("❌ ERROR: No movies available to create EPG!")
        return

    start_time = datetime.datetime.utcnow()
    epg_data = """<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n"""

    movie_pool = movies.copy()  # Copy to shuffle
    random.shuffle(movie_pool)  # Shuffle for randomness

    for i in range(EPG_DURATION_HOURS * 2):  # Assuming ~3 hours per movie
        if not movie_pool:  # Refill if all movies are used
            movie_pool = movies.copy()
            random.shuffle(movie_pool)

        movie = movie_pool.pop()  # Take a random movie

        start_str = start_time.strftime("%Y%m%d%H%M%S") + " +0000"
        end_time = start_time + datetime.timedelta(hours=3)  # Adjust based on movie length
        end_str = end_time.strftime("%Y%m%d%H%M%S") + " +0000"

        epg_data += f"""    <programme start="{start_str}" stop="{end_str}" channel="bihm">
        <title>{movie["title"]}</title>
        <desc>{movie.get("description", "No description available")}</desc>
    </programme>\n"""

        start_time = end_time  # Move to next slot

    epg_data += "</tv>"

    # Write the EPG to file
    with open(EPG_FILE, "w") as f:
        f.write(epg_data)

    # Confirm file was created
    if os.path.exists(EPG_FILE) and os.path.getsize(EPG_FILE) > 0:
        print(f"✅ SUCCESS: EPG generated and saved as {EPG_FILE}")
    else:
        print("❌ ERROR: EPG file is empty!")

def main():
    """Main function to generate EPG and stream movies."""
    movies = load_movies()
    generate_epg(movies)  # Generate EPG before starting the stream

if __name__ == "__main__":
    main()
