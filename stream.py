import json
import os
import subprocess
import shlex
import time
import random

MOVIE_FILE = "movies.json"
LAST_PLAYED_FILE = "last_played.json"
RTMP_URL = os.getenv("RTMP_URL")  # Load RTMP URL from environment variable
OVERLAY = "overlay.png"
MAX_RETRIES = 3  # Maximum retry attempts if no movies are found

if not RTMP_URL:
    print("❌ ERROR: RTMP_URL environment variable is not set!")
    exit(1)

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

def load_played_movies():
    """Load played movies from JSON file."""
    if os.path.exists(LAST_PLAYED_FILE):
        with open(LAST_PLAYED_FILE, "r") as f:
            try:
                return json.load(f).get("played", [])
            except json.JSONDecodeError:
                return []
    return []

def save_played_movies(played_movies):
    """Save played movies to JSON file."""
    with open(LAST_PLAYED_FILE, "w") as f:
        json.dump({"played": played_movies}, f, indent=4)

def stream_movie(movie):
    """Stream a single movie using FFmpeg."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    video_url_escaped = shlex.quote(url)
    overlay_path_escaped = shlex.quote(OVERLAY)
    overlay_text = title.replace(":", r"\:").replace("'", r"\'").replace('"', r'\"')

    command = [
        "ffmpeg",
        "-re",
        "-fflags", "+genpts",
        "-rtbufsize", "32M",
        "-probesize", "1M",
        "-analyzeduration", "500000",
        "-i", video_url_escaped,
        "-i", overlay_path_escaped,
        "-filter_complex",
        f"[0:v][1:v]scale2ref[v0][v1];[v0][v1]overlay=0:0,"
        f"drawtext=text='{overlay_text}':fontcolor=white:fontsize=24:x=20:y=20",
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
        RTMP_URL
    ]

    print(f"🎬 Now Streaming: {title}")

    # Save the currently playing movie
    with open(LAST_PLAYED_FILE, "w") as f:
        json.dump({"played": [title]}, f, indent=4)

    subprocess.run(command)

def main():
    """Main function to stream movies without repetition until all are played."""
    retry_attempts = 0

    while retry_attempts < MAX_RETRIES:
        movies = load_movies()

        if not movies:
            retry_attempts += 1
            print(f"❌ ERROR: No movies available! Retrying ({retry_attempts}/{MAX_RETRIES})...")
            time.sleep(60)
            continue

        retry_attempts = 0  # Reset retry counter on success

        played_movies = load_played_movies()
        all_movie_titles = {movie["title"] for movie in movies}

        while True:
            # Check if all movies have been played
            if set(played_movies) >= all_movie_titles:
                print("🔄 All movies have been played! Restarting playlist...")
                played_movies = []  # Reset the played movie list
                save_played_movies(played_movies)  # Clear the file

            # Filter movies that haven't been played yet
            unplayed_movies = [movie for movie in movies if movie["title"] not in played_movies]

            if not unplayed_movies:
                print("❌ ERROR: No unplayed movies found, but shouldn't happen. Resetting list.")
                played_movies = []
                save_played_movies(played_movies)
                unplayed_movies = movies

            # Shuffle and play unplayed movies
            random.shuffle(unplayed_movies)
            for movie in unplayed_movies:
                stream_movie(movie)
                played_movies.append(movie["title"])
                save_played_movies(played_movies)  # Save progress after each movie

            print("🔄 Restarting after finishing all available movies...")

    print("❌ ERROR: Maximum retry attempts reached. Exiting.")

if __name__ == "__main__":
    main()
