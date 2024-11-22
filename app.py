
TMDB_API_KEY = "0ddbc164201d135fdbdd1e51b8e591ab"

import random
import streamlit as st
import requests
from PIL import Image

# TMDb API key

BASE_URL = "https://api.themoviedb.org/3/"
POSTER_URL = "https://image.tmdb.org/t/p/w500/"

# Main App
st.title("Need a Movie or Show for Tonight?")
st.subheader("Let Me Surprise You 😉✨🎬")
st.markdown("Tired of endless scrolling? Let me pick the perfect movie or TV show for you!")

# Mode Selection using radio button (Movies or TV Shows)
mode = st.radio(
    "Select Mode",
    options=["Movies", "TV Shows"],  # List of options
    help="Choose between Movies or TV Shows"
)

# Priority genres: Horror, Thriller, Mystery
priority_genres = [{"id": 27, "name": "Horror"}, {"id": 53, "name": "Thriller"}, {"id": 9648, "name": "Mystery"}]

# Fetch all genres for both Movies and TV Shows
def fetch_all_genres():
    """Fetches all genres for both movies and TV shows from the TMDb API."""
    movie_genres_response = requests.get(
        f"{BASE_URL}genre/movie/list",
        params={"api_key": TMDB_API_KEY}
    )
    tv_genres_response = requests.get(
        f"{BASE_URL}genre/tv/list",
        params={"api_key": TMDB_API_KEY}
    )
    movie_genres = movie_genres_response.json().get("genres", [])
    tv_genres = tv_genres_response.json().get("genres", [])
    return movie_genres, tv_genres

# Fetch all genres for movies and TV shows
movie_genres, tv_genres = fetch_all_genres()

# Genre Selection: Place priority genres at the top
all_genres = priority_genres + [g for g in movie_genres + tv_genres if g["name"] not in ["Horror", "Thriller", "Mystery"]]

# User selects genres (priority genres will always appear at the top)
selected_genre_names = st.multiselect(
    "Select Genre(s)",
    [g["name"] for g in all_genres],  # All genres, with priority genres at the top
    default=[g["name"] for g in priority_genres],  # Default to the priority genres
    help="Select one or more genres to filter suggestions"
)

# Get the selected genre IDs
selected_genre_ids = []
for genre in movie_genres + tv_genres:
    if genre["name"] in selected_genre_names:
        selected_genre_ids.append(genre["id"])
for genre in priority_genres:
    if genre["name"] in selected_genre_names:
        selected_genre_ids.append(genre["id"])

# Modify movie fetching functions to work with the selected genres and include random year and IMDb score condition
def fetch_movies(genre_ids=None, randomize=False, limit=3):
    """Fetches random movies using TMDb API based on selected genres and adult filter."""
    # Random year between 1999 and current year
    current_year = 2024  # Adjust to the current year dynamically if needed
    random_year = random.randint(1999, current_year)

    params = {
        "api_key": TMDB_API_KEY,
        "vote_average.gte": 6.5,  # IMDb score must be greater than 6
        "include_adult": True,  # Only movies for adults
        "without_genres": "16",  # Exclude animated movies
        "primary_release_year": random_year,  # Random year filter
        "sort_by": "popularity.desc",  # Sort by popularity
    }
    if genre_ids:
        params["with_genres"] = ",".join(map(str, genre_ids))  # Multiple genres
    
    response = requests.get(f"{BASE_URL}discover/movie", params=params)
    movies = response.json().get("results", [])
    
    if randomize:
        movies = random.sample(movies, min(len(movies), limit))
    
    return movies[:limit]  # Return the top 3 random movies

def fetch_tv_shows(genre_ids=None, randomize=False, limit=3):
    """Fetches random TV shows using TMDb API based on selected genres and adult filter."""
    # Random year between 1999 and current year
    current_year = 2024  # Adjust to the current year dynamically if needed
    random_year = random.randint(1999, current_year)

    params = {
        "api_key": TMDB_API_KEY,
        "vote_average.gte": 6.5,  # IMDb score must be greater than 6
        "include_adult": True,  # Only TV shows for adults
        "without_genres": "16",  # Exclude animated TV shows
        "first_air_date.year": random_year,  # Random year filter
        "sort_by": "popularity.desc",  # Sort by popularity
    }
    if genre_ids:
        params["with_genres"] = ",".join(map(str, genre_ids))  # Multiple genres
    
    response = requests.get(f"{BASE_URL}discover/tv", params=params)
    tv_shows = response.json().get("results", [])
    
    if randomize:
        tv_shows = random.sample(tv_shows, min(len(tv_shows), limit))
    
    return tv_shows[:limit]  # Return the top 3 random TV shows

# Surprise Me Button functionality
def fetch_surprise_me_movies_or_tv_shows(is_tv_show=False):
    """Fetch a random movie or TV show from selected genres."""
    return fetch_movies(genre_ids=selected_genre_ids, randomize=True, limit=1) if not is_tv_show else fetch_tv_shows(genre_ids=selected_genre_ids, randomize=True, limit=1)

# Display an image from Unsplash
image_path = "image/dog.jpg"  # Make sure you have this image or update path
img = Image.open(image_path)

# Display the image
st.image(img, caption="A cozy moment 🐾 Photo by vadim kaipov on Unsplash", use_container_width=True)

# "Surprise Me" Button
surprise_me_button = st.button("Surprise Me")
st.markdown(" Whether you're in the mood for something thrilling, spooky, or just a bit of mystery, hit the 'Surprise Me' button, and let the movie magic begin! 🍿🎬")

if surprise_me_button:
    st.header("🎉 Surprise Me!")
    if mode == "Movies":
        random_movie = fetch_surprise_me_movies_or_tv_shows(is_tv_show=False)
        for movie in random_movie:
            release_year = movie.get("release_date", "").split("-")[0]
            st.image(POSTER_URL + movie["poster_path"], width=300)
            st.subheader(f"{movie['title']} ({release_year})")
            st.write(movie["overview"])
            st.write(f"**IMDb Score:** {movie['vote_average']}")
    elif mode == "TV Shows":
        random_tv_show = fetch_surprise_me_movies_or_tv_shows(is_tv_show=True)
        for tv_show in random_tv_show:
            release_year = tv_show.get("first_air_date", "").split("-")[0]
            st.image(POSTER_URL + tv_show["poster_path"], width=300)
            st.subheader(f"{tv_show['name']} ({release_year})")
            st.write(tv_show["overview"])
            st.write(f"**IMDb Score:** {tv_show['vote_average']}")

# Submit Button to fetch results based on selected genres
submit_button = st.button("Submit")
st.markdown("Click 'Submit' to discover 3 more exciting suggestions in your chosen genre!")

if submit_button:
    if mode == "Movies" and selected_genre_names:
        st.header(f"🎥 Movie Suggestions")
        movies = fetch_movies(genre_ids=selected_genre_ids, randomize=True, limit=3)
        for movie in movies:
            release_year = movie.get("release_date", "").split("-")[0]
            st.image(POSTER_URL + movie["poster_path"], width=300)
            st.subheader(f"{movie['title']} ({release_year})")
            st.write(movie["overview"])
            st.write(f"**IMDb Score:** {movie['vote_average']}")
    
    elif mode == "TV Shows" and selected_genre_names:
        st.header(f"📺 TV Show Suggestions")
        tv_shows = fetch_tv_shows(genre_ids=selected_genre_ids, randomize=True, limit=3)
        for tv_show in tv_shows:
            release_year = tv_show.get("first_air_date", "").split("-")[0]
            st.image(POSTER_URL + tv_show["poster_path"], width=300)
            st.subheader(f"{tv_show['name']} ({release_year})")
            st.write(tv_show["overview"])
            st.write(f"**IMDb Score:** {tv_show['vote_average']}")
