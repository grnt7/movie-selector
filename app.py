import streamlit as st
import requests
import random
import pandas as pd  # Imported to initialize the empty DataFrame securely
# Cleanly import your exact backend functions
from project import get_tmdb_token, get_genre_list, build_mixed_recommendations

# 1. Page Configuration
st.set_page_config(page_title="TMDB Movie Selector", page_icon="🎬", layout="centered")

st.title("🎬 TMDB Movie Selector")
st.write("Find top-rated movies based on your favorite genres instantly.")

# Declare token beforehand to avoid unbound analysis alerts
token = ""

# 2. Authenticate securely
try:
    token = get_tmdb_token()
except SystemExit:
    st.error("🔑 API Token Missing! Please set the `TMDB_READ_ACCESS_TOKEN` environment variable in your terminal.")
    st.stop()

# 3. Dynamic Selection Setup
st.header("Search Filters")

# Fallback basic list if token handshake experiences network delays
genres_available = ["Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Romance"]
genres_map = {}

try:
    # Your backend returns a clean dict[str, int] mapping names to IDs
    genres_map = get_genre_list(token)
    if genres_map:
        genres_available = list(genres_map.keys())
except Exception:
    pass

selected_genre_name = st.selectbox("Choose a Movie Genre:", genres_available)
limit = st.slider("How many movies would you like to display?", min_value=1, max_value=20, value=10)

# 4. Trigger Search Action
if st.button("Discover Movies", type="primary"):
    with st.spinner("Compiling recommendations from TMDB..."):
        
        # Translate the text selection into your backend's integer ID format
        genre_id = genres_map.get(selected_genre_name, 35) # Defaults to comedy if missing
        rng = random.Random()
        
        # FIX FOR UNBOUND DF: Initialize an empty DataFrame so it always exists
        df = pd.DataFrame()
        
        try:
            # Executes your exact backend recommendation pipeline
            df = build_mixed_recommendations(genre_id, limit, token, rng)
        except Exception as e:
            st.error(f"Error connecting to TMDB API: {e}")
            st.stop()
            
        if df.empty:
            st.warning("No matching movies found for this collection context.")
        else:
            st.success(f"Found your custom mix of {len(df)} movies!")
            st.divider()
            
           # 5. Visual Display Loop iterating over the DataFrame records
            for _, movie in df.iterrows():
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Safely extract the mapped string path
                    path = movie.get("poster_path")
                    
                    # Verify it's a valid non-empty string path from TMDB
                    if path and isinstance(path, str) and path.startswith("/"):
                        full_poster_url = f"https://image.tmdb.org/t/p/w500{path}"
                        st.image(full_poster_url, use_container_width=True)
                    else:
                        st.image("https://placehold.co/500x750?text=No+Poster", use_container_width=True)
                
                with col2:
                    st.subheader(f"{movie.get('Title', 'Unknown Title')} ({movie.get('Year', 'N/A')})")
                    st.caption(f"⭐ Rating: {movie.get('Rating', 0.0)}/10 | 📦 Origin: {movie.get('Source', 'Discovery')}")
                    st.write(movie.get("overview", "No description text pulled for this record."))
                    st.divider()