import json
import datetime
import random
import requests

# 🔹 OMDB API Key
OMDB_API_KEY = "a3b171bc"

# 🔹 Load movie list
with open("movies.json", "r") as file:
    movies = json.load(file)

# 🔹 Shuffle movies for variety
random.shuffle(movies)

# 🔹 Generate a 24-hour schedule
schedule = []
start_time = datetime.datetime.utcnow()

for movie in movies:
    title = movie["title"]
    url = movie["url"]

    # 🔹 Get movie duration from OMDB
    imdb_title = title.split("(")[0].strip()
    response = requests.get(f"http://www.omdbapi.com/?t={imdb_title}&apikey={OMDB_API_KEY}")
    movie_data = response.json()
    
    if "Runtime" in movie_data:
        duration_minutes = int(movie_data["Runtime"].split(" ")[0])
    else:
        duration_minutes = 120  # Default to 2 hours if no data
    
    duration_seconds = duration_minutes * 60
    end_time = start_time + datetime.timedelta(seconds=duration_seconds)

    schedule.append({
        "title": title,
        "url": url,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": duration_seconds
    })

    start_time = end_time

    if start_time >= datetime.datetime.utcnow() + datetime.timedelta(hours=24):
        break  # Stop once we fill 24 hours

# 🔹 Save to now_showing.json
with open("now_showing.json", "w") as file:
    json.dump(schedule, file, indent=4)

print("✅ New 24-hour schedule generated!")
