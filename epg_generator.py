import os
import json
import datetime
import random

# Constants
EPG_FILE = "epg.xml"
MOVIE_FILE = "movies.json"
TOTAL_MOVIES = 6  # Number of movies for EPG

def load_movies():
    """Load movies from a JSON file."""
    if not os.path.exists(MOVIE_FILE):
        print(f"❌ ERROR: {MOVIE_FILE} not found!")
        return []

    try:
        with open(MOVIE_FILE, "r", encoding="utf-8") as f:
            movies = json.load(f)
        if not isinstance(movies, list) or not movies:
            print("❌ ERROR: Invalid movie data format!")
            return []
        return movies
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Failed to parse {MOVIE_FILE}! {e}")
        return []

def generate_epg(movies):
    """Generate a new EPG XML file for the next 6 hours with selected movies."""
    if not movies:
        print("❌ ERROR: No movies available for EPG!")
        return []

    start_time = datetime.datetime.utcnow()
    epg_data = """<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n"""

    total_movies = min(TOTAL_MOVIES, len(movies))
    if total_movies == 0:
        print("❌ ERROR: Not enough movies to generate EPG!")
        return []

    try:
        selected_movies = random.sample(movies, total_movies)  # Randomly select movies
    except ValueError as e:
        print(f"❌ ERROR: {e} (Not enough movies in {MOVIE_FILE})")
        return []

    schedule = []  # Store scheduled movies

    for movie in selected_movies:
        title = movie.get("title", "Unknown Title")
        description = movie.get("category", "No description available")  # Using category as description
        image = movie.get("image", "")
        url = movie.get("url", "#")
        start_str = start_time.strftime("%Y%m%d%H%M%S +0000")
        end_time = start_time + datetime.timedelta(minutes=180)  # Approx. 3-hour runtime
        end_str = end_time.strftime("%Y%m%d%H%M%S +0000")

        epg_data += f"""    <programme start="{start_str}" stop="{end_str}" channel="bihm">
        <title>{title}</title>
        <desc>{description}</desc>
        <icon src="{image}"/>
        <link>{url}</link>
    </programme>\n"""

        schedule.append(movie)
        start_time = end_time  # Move to next slot

    epg_data += "</tv>"

    try:
        with open(EPG_FILE, "w", encoding="utf-8") as f:
            f.write(epg_data)
        print(f"✅ SUCCESS: EPG generated with {len(schedule)} movies")
    except IOError as e:
        print(f"❌ ERROR: Failed to write EPG file! {e}")

    if os.path.exists(EPG_FILE) and os.path.getsize(EPG_FILE) > 0:
        print(f"✅ SUCCESS: EPG file created at {EPG_FILE}")
    else:
        print("❌ ERROR: EPG file is empty after writing!")

    return schedule

if __name__ == "__main__":
    movies = load_movies()
    generate_epg(movies)
