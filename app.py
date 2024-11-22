TMDB_API_KEY = "0ddbc164201d135fdbdd1e51b8e591ab"

import random
import streamlit as st
import requests

# TMDb API key
BASE_URL = "https://api.themoviedb.org/3/"
POSTER_URL = "https://image.tmdb.org/t/p/w500/"

# Main App
st.title("Need a Movie or Show for Tonight? Let Me Surprise You 😉✨🎬")
st.markdown("Tired of endless scrolling? Let me pick the perfect movie or TV show for you!")

# Mode Selection using radio button (Movies or TV Shows)
mode = st.radio(
    "Select Mode",
    options=["Movies", "TV Shows"],  # List of options
    help="Choose between Movies or TV Shows"
)

# Fetch all genres
def fetch_all_genres():
    """Fetches all genres from the TMDb API."""
    response = requests.get(
        f"{BASE_URL}genre/movie/list",
        params={"api_key": TMDB_API_KEY}
    )
    genres = response.json().get("genres", [])
    return genres

# Define the specific genres to focus on: Horror, Thriller, and Mystery
priority_genres = [{"id": 27, "name": "Horror"}, {"id": 53, "name": "Thriller"}, {"id": 9648, "name": "Mystery"}]

# Use the priority_genres list directly for the genre selection filter
selected_genre_names = st.multiselect(
    "Select Genre(s)",
    [g["name"] for g in priority_genres],
    default=[g["name"] for g in priority_genres],  # Default genres
    help="Select one or more genres to filter suggestions",
)

# Determine the selected genre IDs based on user input
selected_genre_ids = [g["id"] for g in priority_genres if g["name"] in selected_genre_names]

# Modify movie fetching functions to work with the selected genres
def fetch_movies(genre_id=None, randomize=False, limit=3):
    """Fetches movies using TMDb API based on genre and adult filter."""
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50,
        "include_adult": True,  # Only movies for adults
        "without_genres": "16",  # Exclude animated movies
        "primary_release_date.gte": "1999-01-01",  # Filter movies released after 1999
    }
    if genre_id:
        params["with_genres"] = genre_id

    response = requests.get(f"{BASE_URL}discover/movie", params=params)
    movies = response.json().get("results", [])
    
    if randomize:
        movies = random.sample(movies, min(len(movies), limit))
    
    return movies[:limit]  # Only return the top 3 movies

def fetch_tv_shows(genre_id=None, randomize=False, limit=3):
    """Fetches TV shows using TMDb API based on genre and adult filter."""
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "vote_average.desc",
        "vote_count.gte": 50,
        "include_adult": True,  # Only TV shows for adults
        "without_genres": "16",  # Exclude animated TV shows
        "first_air_date.gte": "1999-01-01",  # Filter TV shows released after 1999
    }
    if genre_id:
        params["with_genres"] = genre_id

    response = requests.get(f"{BASE_URL}discover/tv", params=params)
    tv_shows = response.json().get("results", [])
    
    if randomize:
        tv_shows = random.sample(tv_shows, min(len(tv_shows), limit))
    
    return tv_shows[:limit]  # Only return the top 3 TV shows

# Modify the Surprise Me functionality to focus on the three genres only
def fetch_surprise_me_movies_or_tv_shows(is_tv_show=False):
    """Fetch a random movie or TV show from Horror, Thriller, or Mystery genres."""
    genre_ids = [27, 53, 9648]  # Horror, Thriller, Mystery
    genre_id = random.choice(genre_ids)
    if is_tv_show:
        return fetch_tv_shows(genre_id=genre_id, randomize=True, limit=1)
    else:
        return fetch_movies(genre_id=genre_id, randomize=True, limit=1)


# Fetch all genres for Movies and TV Shows
genres = fetch_all_genres()

# "Surprise Me" Button
surprise_me_button = st.button("Surprise Me")
st.markdown(" Whether you're in the mood for something thrilling, spooky, or just a bit of mystery, I've got you covered. Hit the 'Surprise Me' button, and let the movie magic begin! 🍿🎬")

from PIL import Image
# Display an image from Unsplash
image_path = "image/dog.jpg"
img = Image.open(image_path)

# Display the image
st.image(img, caption="A cozy moment 🐾 Photo by vadim kaipov on Unsplash", use_container_width=True)

# "Surprise Me" Button (Focuses on the three genres)
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

# Submit Button to fetch results
submit_button = st.button("Submit")

st.markdown("Click 'Submit' to discover 3 more exciting suggestions in your chosen genre!")
# Submit Button to fetch results based on selected genres
if submit_button:
    if mode == "Movies" and selected_genre_names:
        st.header(f"🎥 Movie Suggestions")
        movies = fetch_movies(genre_id=selected_genre_ids, randomize=True, limit=3)
        for movie in movies:
            release_year = movie.get("release_date", "").split("-")[0]
            st.image(POSTER_URL + movie["poster_path"], width=300)
            st.subheader(f"{movie['title']} ({release_year})")
            st.write(movie["overview"])
            st.write(f"**IMDb Score:** {movie['vote_average']}")
    
    elif mode == "TV Shows" and selected_genre_names:
        st.header(f"📺 TV Show Suggestions")
        tv_shows = fetch_tv_shows(genre_id=selected_genre_ids, randomize=True, limit=3)
        for tv_show in tv_shows:
            release_year = tv_show.get("first_air_date", "").split("-")[0]
            st.image(POSTER_URL + tv_show["poster_path"], width=300)
            st.subheader(f"{tv_show['name']} ({release_year})")
            st.write(tv_show["overview"])
            st.write(f"**IMDb Score:** {tv_show['vote_average']}")
