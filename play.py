import json
import re
import random

MOVIE_FILE = "movies.json"
PLAY_FILE = "play.json"

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def extract_show(title):
    m = re.match(r"(.+?)\sS\d{2}E\d{2}", title)
    return m.group(1).strip() if m else None

def extract_season_ep(title):
    m = re.search(r"S(\d{2})E(\d{2})", title)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)

def group_by_show(movies):
    shows = {}
    for ep in movies:
        show = extract_show(ep["title"])
        if show:
            shows.setdefault(show, []).append(ep)

    # Sort by season + episode
    for show in shows:
        shows[show].sort(key=lambda x: extract_season_ep(x["title"]))
    return shows

def get_next_episode(episodes, current_title):
    """Return the next episode object or None if at the end."""
    for i, ep in enumerate(episodes):
        if ep["title"] == current_title:
            return episodes[i + 1] if i + 1 < len(episodes) else None
    return None

def pick_new_show(shows, exclude=None):
    keys = list(shows.keys())
    if exclude in keys:
        keys.remove(exclude)
    return random.choice(keys)

def update_play_json():
    all_movies = load_json(MOVIE_FILE)
    play = load_json(PLAY_FILE)
    shows = group_by_show(all_movies)

    # ---------------------------------------------
    # CASE 1: play.json EMPTY → initialize first 10
    # ---------------------------------------------
    if not play:
        show = random.choice(list(shows.keys()))
        episodes = shows[show][:10]
        save_json(PLAY_FILE, episodes)
        print(f"Initialized play.json with 10 episodes from {show}")
        return

    # ---------------------------------------------
    # CASE 2: Remove first episode (played by stream.py)
    # ---------------------------------------------
    first_episode = play.pop(0)
    first_show = extract_show(first_episode["title"])
    remaining_show_episodes = shows[first_show]

    # ---------------------------------------------
    # Find the next chronological episode
    # ---------------------------------------------
    next_ep = get_next_episode(remaining_show_episodes, first_episode["title"])

    if next_ep:
        # Append next episode of same series
        play.append(next_ep)
        save_json(PLAY_FILE, play)
        print(f"Inserted next episode: {next_ep['title']}")
        return

    # ---------------------------------------------
    # CASE 3: Season finished → switch to NEW random show
    # ---------------------------------------------
    new_show = pick_new_show(shows, exclude=first_show)
    next_list = shows[new_show]

    if next_list:
        play.append(next_list[0])  # Episode 1 of new show
        save_json(PLAY_FILE, play)
        print(f"Season ended. Switched to new show: {new_show}")
        return

if __name__ == "__main__":
    update_play_json()
