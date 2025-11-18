import json
import random

MOVIE_FILE = "movies.json"
PLAY_FILE = "play.json"
SELECTION_COUNT = 15  # Number of movies to select each run


def load_json(path):
    """Load a JSON list safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_json(path, data):
    """Save a JSON list with formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def update_play_json():
    """Select 15 unique movies that haven't been picked yet."""
    all_movies = load_json(MOVIE_FILE)
    played_movies = load_json(PLAY_FILE)

    # Exclude already used items
    remaining = [m for m in all_movies if m not in played_movies]

    # If not enough remaining, reset pool
    if len(remaining) < SELECTION_COUNT:
        print("Cycle complete — restarting with full movie list.")
        remaining = all_movies

    # Choose 15 random movies
    selected = random.sample(remaining, SELECTION_COUNT)

    # Save results
    save_json(PLAY_FILE, selected)
    print(f"Updated play.json with {SELECTION_COUNT} movies.")


if __name__ == "__main__":
    update_play_json()
