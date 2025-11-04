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

    # ✅ Global mode → everything 엔드포인트 사용
    if country == "global":
        base_url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic if topic.strip() else "trending",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 15,
            "apiKey": api_key
        }

    # ✅ 특정 국가 선택 → top-headlines 사용
    else:
        base_url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "pageSize": 15,
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
                "Source": a["source"]["name"],
                "Published": a["publishedAt"][:10] if a.get("publishedAt") else "",
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

        # ✅ URL을 클릭 가능한 링크로 변환
        news_df["Title"] = news_df.apply(
            lambda x: f'<a href="{x["URL"]}" target="_blank">{x["Title"]}</a>', axis=1
        )

        # ✅ 불필요한 URL 컬럼 제거
        news_df_display = news_df[["Title", "Source", "Published"]]

        # ✅ HTML로 출력 (링크 활성화)
        st.write(news_df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

    else:
        st.warning("No news found or invalid API key.")

# ----------------------------------------------------------
# ℹ️ Footer
# ----------------------------------------------------------
st.markdown("""
---
Made with ❤️ using [NewsAPI](https://newsapi.org)
""")
