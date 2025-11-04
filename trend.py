import streamlit as st
import requests
import pandas as pd

# 🎨 Streamlit setup
st.set_page_config(page_title="Trend News Dashboard", page_icon="📰", layout="wide")
st.title("📰 Trend News Dashboard")
st.write("Explore the **latest news** on your favorite topics in real time!")

# ----------------------------------------------------------
# 🧠 Input: API key & Search topic
# ----------------------------------------------------------
st.sidebar.header("🔑 API Key & Settings")
user_api_key = st.sidebar.text_input("Enter your NewsAPI key:", type="password")
topic = st.text_input("Enter a topic to search (e.g. AI, Climate Change, Space):", "AI")

# ----------------------------------------------------------
# 📰 Fetch News Articles
# ----------------------------------------------------------
def get_news(topic, api_key):
    """Fetch latest news articles for the given topic using NewsAPI."""
    if not api_key:
        st.warning("Please enter your NewsAPI key in the sidebar.")
        return pd.DataFrame()

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={topic}&sortBy=publishedAt&language=en&apiKey={api_key}"
    )
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        st.error(f"Error fetching news: {data.get('message', 'Unknown error')}")
        return pd.DataFrame()

    if "articles" in data:
        articles = data["articles"][:10]
        return pd.DataFrame([
            {
                "Title": a["title"],
                "Source": a["source"]["name"],
                "Published": a["publishedAt"],
                "URL": a["url"]
            }
            for a in articles if a["title"]
        ])
    else:
        return pd.DataFrame()

# ----------------------------------------------------------
# 📈 Display Results
# ----------------------------------------------------------
if st.button("Search 🔍"):
    news_df = get_news(topic, user_api_key)
    if not news_df.empty:
        st.subheader(f"📰 Latest News on '{topic}'")
        st.dataframe(news_df)
    else:
        st.warning("No news found or invalid API key.")

# ----------------------------------------------------------
# ℹ️ Footer
# ----------------------------------------------------------
st.markdown("""
---
Made with ❤️ using [NewsAPI](https://newsapi.org)
""")
