import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# 🎨 Streamlit setup
st.set_page_config(page_title="TrendAPI Dashboard", page_icon="🔥", layout="wide")
st.title("🔥 TrendAPI Dashboard")
st.write("Explore trending **News** 📰 and **Music** 🎵 from the same topic!")

# ----------------------------------------------------------
# 🔑 Load API keys securely
# ----------------------------------------------------------
NEWS_API_KEY = st.secrets["api_keys"]["newsapi_key"]
SPOTIFY_CLIENT_ID = st.secrets["api_keys"]["spotify_client_id"]
SPOTIFY_CLIENT_SECRET = st.secrets["api_keys"]["spotify_client_secret"]

# ----------------------------------------------------------
# 🎵 Initialize Spotify API client
# ----------------------------------------------------------
spotify_auth = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = Spotify(client_credentials_manager=spotify_auth)

# ----------------------------------------------------------
# 🧠 Input: Search topic
# ----------------------------------------------------------
topic = st.text_input("Enter a topic to explore trends (e.g. AI, Taylor Swift, Climate Change):", "AI")

# ----------------------------------------------------------
# 📰 Fetch News Articles
# ----------------------------------------------------------
def get_news(topic):
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "articles" in data:
        articles = data["articles"][:10]
        return pd.DataFrame([{
            "Title": a["title"],
            "Source": a["source"]["name"],
            "Published": a["publishedAt"],
            "URL": a["url"]
        } for a in articles])
    else:
        return pd.DataFrame()

# ----------------------------------------------------------
# 🎧 Fetch Spotify Trends (Artists / Tracks)
# ----------------------------------------------------------
def get_spotify_trends(topic):
    results = spotify.search(q=topic, type="track", limit=10)
    tracks = results["tracks"]["items"]
    data = []
    for t in tracks:
        data.append({
            "Track": t["name"],
            "Artist": ", ".join([a["name"] for a in t["artists"]]),
            "Popularity": t["popularity"],
            "Album": t["album"]["name"],
            "URL": t["external_urls"]["spotify"]
        })
    return pd.DataFrame(data)

# ----------------------------------------------------------
# 📈 Display Results
# ----------------------------------------------------------
if st.button("Search 🔍"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📰 Latest News")
        news_df = get_news(topic)
        if not news_df.empty:
            st.dataframe(news_df)
        else:
            st.warning("No news articles found.")

    with col2:
        st.subheader("🎵 Trending Tracks on Spotify")
        tracks_df = get_spotify_trends(topic)
        if not tracks_df.empty:
            fig = px.bar(tracks_df, x="Popularity", y="Track", color="Artist",
                         orientation="h", title=f"Top Tracks Related to '{topic}'")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(tracks_df)
        else:
            st.warning("No Spotify results found.")

# ----------------------------------------------------------
# ℹ️ Footer
# ----------------------------------------------------------
st.markdown("""
---
Made with ❤️ using [NewsAPI](https://newsapi.org) and [Spotify API](https://developer.spotify.com)
""")
