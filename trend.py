import streamlit as st
import requests
import pandas as pd

# 🎨 Streamlit setup
st.set_page_config(page_title="Global Trend News Dashboard", page_icon="📰", layout="wide")
st.title("📰 Global Trend News Dashboard")
st.write("Stay updated with the latest headlines from around the world!")

# ----------------------------------------------------------
# 🧩 Sidebar: API Key + Info
# ----------------------------------------------------------
st.sidebar.header("🔑 NewsAPI Settings")

st.sidebar.markdown("""
**👉 How to get a NewsAPI Key**
1. Visit [NewsAPI.org](https://newsapi.org/register)
2. Sign up for a free account
3. Go to the [Dashboard](https://newsapi.org/account)
4. Copy your **API key** and paste it below 👇
""")

user_api_key = st.sidebar.text_input("Enter your NewsAPI key:", type="password")

# ----------------------------------------------------------
# 🌍 Country selection
# ----------------------------------------------------------
country_options = {
    "us": "🇺🇸 United States",
    "gb": "🇬🇧 United Kingdom",
    "kr": "🇰🇷 South Korea",
    "jp": "🇯🇵 Japan",
    "fr": "🇫🇷 France",
    "de": "🇩🇪 Germany",
    "in": "🇮🇳 India",
    "au": "🇦🇺 Australia",
    "ca": "🇨🇦 Canada",
    "br": "🇧🇷 Brazil"
}

country = st.sidebar.selectbox("🌎 Choose a country:", options=list(country_options.keys()),
                               format_func=lambda x: country_options[x])

topic = st.text_input("Enter a topic or leave blank to see top headlines:", "")

# ----------------------------------------------------------
# 📰 Fetch News Articles
# ----------------------------------------------------------
def get_news(country, topic, api_key):
    """Fetch latest news articles from NewsAPI."""
    if not api_key:
        st.warning("Please enter your NewsAPI key in the sidebar.")
        return pd.DataFrame()

    if topic.strip():
        url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&apiKey={api_key}"
    else:
        url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}"

    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        st.error(f"Error fetching news: {data.get('message', 'Unknown error')}")
        return pd.DataFrame()

    if "articles" in data and data["articles"]:
        articles = data["articles"][:15]
        return pd.DataFrame([
            {
                "Title": a["title"],
                "Source": a["source"]["name"],
                "Published": a["publishedAt"][:10],
                "URL": a["url"]
            }
            for a in articles if a.get("title")
        ])
    else:
        return pd.DataFrame()

# ----------------------------------------------------------
# 📈 Display Results
# ----------------------------------------------------------
if st.button("Search 🔍"):
    news_df = get_news(country, topic, user_api_key)
    if not news_df.empty:
        st.subheader(f"🗞️ Top News from {country_options[country]}")
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
