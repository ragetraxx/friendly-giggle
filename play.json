import json
import random
import time

MOVIE_FILE = "movie.json"  # Source file
PLAY_FILE = "play.json"  # Destination file
INTERVAL = 5 * 60 * 60  # 5 hours in seconds

def load_movies():
    """Load movies from movie.json"""
    try:
        with open(MOVIE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error: {MOVIE_FILE} not found or invalid JSON.")
        return []

def save_play_movies(movies):
    """Save selected movies to play.json"""
    with open(PLAY_FILE, "w", encoding="utf-8") as file:
        json.dump(movies, file, indent=4)

def update_play_json():
    """Randomly select 5 movies and update play.json"""
    movies = load_movies()
    if not movies:
        print("No movies available to select.")
        return

    selected_movies = random.sample(movies, min(5, len(movies)))
    save_play_movies(selected_movies)
    print("Updated play.json with 5 movies.")

if __name__ == "__main__":
    update_play_json()  # Run once 
