import json
import os
import subprocess
import shlex
import time
import random

MOVIE_FILE = "movies.json"
LAST_PLAYED_FILE = "last_played.json"
RTMP_URL = "rtmp://ssh101.bozztv.com:1935/ssh101/bihm"
OVERLAY = "overlay.png"

def load_movies():
    """Load movies from JSON file."""
    if not os.path.exists(MOVIE_FILE):
        print(f"❌ ERROR: {MOVIE_FILE} not found!")
        return []

    with open(MOVIE_FILE, "r") as f:
        try:
            movies = json.load(f)
            return movies if movies else []
        except json.JSONDecodeError:
            print("❌ ERROR: Failed to parse movies.json!")
            return []

def load_played_movies():
    """Load played movies from last_played.json or initialize if empty."""
    if os.path.exists(LAST_PLAYED_FILE):
        with open(LAST_PLAYED_FILE, "r") as f:
            try:
                data = json.load(f)
                return data.get("played", [])
            except (json.JSONDecodeError, TypeError):
                return []
    return []

def save_played_movies(played_movies, current_movie=None):
    """Save played movies to last_played.json, including the currently playing movie."""
    data = {"played": played_movies}
    if current_movie:
        data["current"] = current_movie  # Save currently playing movie

    with open(LAST_PLAYED_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_next_movie():
    """Get a random unplayed movie, reset if all are played."""
    movies = load_movies()
    played_movies = load_played_movies()

    all_movie_titles = {movie["title"] for movie in movies}
    
    # Reset played movies if all movies have been played
    if set(played_movies) >= all_movie_titles:
        print("🔄 All movies have been played! Resetting playlist...")
        played_movies = []
        save_played_movies(played_movies)  # Clear last_played.json

    # Get unplayed movies
    unplayed_movies = [movie for movie in movies if movie["title"] not in played_movies]

    if not unplayed_movies:
        print("⚠️ No unplayed movies left, restarting the list...")
        played_movies = []
        unplayed_movies = movies

    # Pick a random movie
    next_movie = random.choice(unplayed_movies)
    return next_movie, played_movies

def stream_movie(movie, played_movies):
    """Stream a movie using FFmpeg."""
    title = movie.get("title", "Unknown Title")
    url = movie.get("url")

    if not url:
        print(f"❌ ERROR: Missing URL for movie '{title}'")
        return

    # Add the movie to played list and save progress
    played_movies.append(title)
    save_played_movies(played_movies, title)

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
    subprocess.run(command)

def main():
    """Main function to continuously stream movies without repetition."""
    while True:
        next_movie, played_movies = get_next_movie()
        stream_movie(next_movie, played_movies)

if __name__ == "__main__":
    main()
