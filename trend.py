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
# 🌍 Country selection (updated)
# ----------------------------------------------------------
country_options = {
    "global": "🌍 Global",
    "us": "🇺🇸 United States",
    "gb": "🇬🇧 United Kingdom",
    "jp": "🇯🇵 Japan",
    "in": "🇮🇳 India"
}

country = st.sidebar.selectbox("🌎 Choose a region:", options=list(country_options.keys()),
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

    if country == "global":
        base_url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic if topic.strip() else "trending",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": api_key
        }
    else:
        base_url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "pageSize": 10,
            "apiKey": api_key
        }
        if topic.strip():
            params["q"] = topic

    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code != 200:
        st.error(f"Error fetching news: {data.get('message', 'Unknown error')}")
        return pd.DataFrame()

    if "articles" in data and data["articles"]:
        articles = data["articles"]
        return pd.DataFrame([
            {
                "Title": a["title"],
                "Summary": a.get("description") or a.get("content") or "",
                "Source": a["source"]["name"],
                "Published": a["publishedAt"][:10] if a.get("publishedAt") else "",
                "URL": a["url"]
            }
            for a in articles if a.get("title")
        ])
    else:
        return pd.DataFrame()

# ----------------------------------------------------------
# 📈 Display Results (with summaries)
# ----------------------------------------------------------
if st.button("Search 🔍"):
    news_df = get_news(country, topic, user_api_key)
    if not news_df.empty:
        st.subheader(f"🗞️ Top News from {country_options[country]}")

        # ✅ HTML 구성
        html_content = ""
        for _, row in news_df.iterrows():
            summary = row["Summary"][:200] + "..." if len(row["Summary"]) > 200 else row["Summary"]
            html_content += f"""
            <div style="margin-bottom: 1.2em; padding: 0.8em; border-radius: 10px; background-color: #f9f9f9;">
                <a href="{row['URL']}" target="_blank" style="font-size: 1.05em; font-weight: 600; color: #1a73e8; text-decoration: none;">
                    {row['Title']}
                </a><br>
                <span style="font-size: 0.9em; color: #555;">{summary}</span><br>
                <span style="font-size: 0.8em; color: #888;">📅 {row['Published']} | 🏷️ {row['Source']}</span>
            </div>
            """

        st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.warning("No news found or invalid API key.")

# ----------------------------------------------------------
# ℹ️ Footer
# ----------------------------------------------------------
st.markdown("""
---
Made with ❤️ using [NewsAPI](https://newsapi.org)
""")
