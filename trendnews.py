import streamlit as st
import requests
import pandas as pd
import re
from openai import OpenAI

# ----------------------------------------------------------
# 🎨 Streamlit setup
# ----------------------------------------------------------
st.set_page_config(page_title="Global Trend News Dashboard", page_icon="📰", layout="wide")
st.title("📰 Global Trend News Dashboard")
st.write("Stay updated with the latest headlines from around the world!")

# ----------------------------------------------------------
# 🧩 Sidebar: API Key + Info
# ----------------------------------------------------------
st.sidebar.header("🔑 API Settings")

# 🧾 NewsAPI 안내
st.sidebar.markdown("""
**🗞 How to get a NewsAPI Key**
1. Visit [NewsAPI.org](https://newsapi.org/register)
2. Sign up for a free account
3. Copy your **API key** and paste it below 👇
""")
news_api_key = st.sidebar.text_input("Enter your NewsAPI key:", type="password")

# 💡 OpenAI API Key 안내
st.sidebar.markdown("""
**🧠 How to get an OpenAI API Key**
1. Visit [OpenAI API Keys](https://platform.openai.com/account/api-keys)
2. Log in and click “Create new secret key”
3. Copy and paste it below 👇
""")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API key (for GPT summaries):", type="password")

# GPT 요약 기능 On/Off
use_gpt_summary = st.sidebar.toggle("✨ Enable GPT Summaries", value=False)

# ----------------------------------------------------------
# 🌍 Country selection (includes Global)
# ----------------------------------------------------------
country_options = {
    "global": "🌍 Global",
    "us": "🇺🇸 United States",
    "gb": "🇬🇧 United Kingdom",
    "jp": "🇯🇵 Japan",
    "in": "🇮🇳 India"
}

country = st.sidebar.selectbox(
    "🌎 Choose a region:",
    options=list(country_options.keys()),
    format_func=lambda x: country_options[x]
)

# 🔍 Topic input
topic = st.text_input("Enter a topic or leave blank to see top headlines:", "")

# ----------------------------------------------------------
# 🧹 Text cleaner
# ----------------------------------------------------------
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"window\.open\(.*?\)", "", text)
    text = re.sub(r"onclick=.*?(;|\"|')", "", text)
    text = re.sub(r"javascript:.*?(;|\"|')", "", text)
    text = re.sub(r"\[\+\d+\s*chars\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ----------------------------------------------------------
# 📰 Fetch News
# ----------------------------------------------------------
def get_news(country, topic, api_key, page_size=10):
    if not api_key:
        st.warning("Please enter your NewsAPI key in the sidebar.")
        return pd.DataFrame()

    if country == "global":
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": topic if topic.strip() else "trending",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": api_key
        }
    else:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "pageSize": page_size,
            "apiKey": api_key
        }
        if topic.strip():
            params["q"] = topic

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        st.error(f"Error fetching news: {data.get('message', 'Unknown error')}")
        return pd.DataFrame()

    if "articles" not in data or not data["articles"]:
        return pd.DataFrame()

    articles = data["articles"]
    return pd.DataFrame([
        {
            "Title": a["title"],
            "Summary": clean_text(a.get("description") or a.get("content") or ""),
            "Source": a["source"]["name"],
            "Published": a["publishedAt"][:10] if a.get("publishedAt") else "",
            "URL": a["url"]
        }
        for a in articles if a.get("title")
    ])

# ----------------------------------------------------------
# 🧠 GPT Summarization
# ----------------------------------------------------------
def summarize_with_gpt(text, client):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes news clearly and concisely."},
                {"role": "user", "content": f"Summarize this news article in 2 sentences:\n{text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # OpenAI quota or 429 error → handled globally
        raise e

# ----------------------------------------------------------
# 📈 Display Results
# ----------------------------------------------------------
if st.button("Search 🔍"):
    news_df = get_news(country, topic, news_api_key)
    if not news_df.empty:
        st.subheader(f"🗞️ Top News from {country_options[country]}")

        openai_error_shown = False
        client = None
        if use_gpt_summary and openai_api_key:
            client = OpenAI(api_key=openai_api_key)

        for _, row in news_df.iterrows():
            title_html = f"""
            <div style="margin-bottom: 1.2em; padding: 0.8em; border-radius: 10px; background-color: #f9f9f9;">
                <a href="{row['URL']}" target="_blank" style="font-size: 1.05em; font-weight: 600; color: #1a73e8; text-decoration: none;">
                    {row['Title']}
                </a><br>
            """
            st.markdown(title_html, unsafe_allow_html=True)

            # GPT 요약 시도
            if use_gpt_summary and client:
                try:
                    summary_text = summarize_with_gpt(row["Summary"], client)
                    st.markdown(f"🧠 **GPT 요약:** {summary_text}")
                except Exception as e:
                    if not openai_error_shown:
                        st.error("⚠️ OpenAI quota exceeded or API error. Showing original summaries instead.")
                        openai_error_shown = True
                    st.markdown(f"📝 **Summary:** {row['Summary']}")
            else:
                st.markdown(f"📝 **Summary:** {row['Summary']}")

            st.markdown(f"📅 {row['Published']} | 🏷️ {row['Source']}")
            st.markdown("---")
    else:
        st.warning("No news found or invalid API key.")

# ----------------------------------------------------------
# ℹ️ Footer
# ----------------------------------------------------------
st.markdown("""
---
Made with ❤️ using [NewsAPI](https://newsapi.org)
""")
