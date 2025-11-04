import streamlit as st
import requests
import re
from openai import OpenAI

# ---- App Title ----
st.set_page_config(page_title="Global Trend News Dashboard", page_icon="📰", layout="wide")
st.title("📰 Global Trend News Dashboard")

# ---- Sidebar: Settings ----
st.sidebar.header("🔑 NewsAPI Settings")
st.sidebar.markdown("""
### 👉 How to get a NewsAPI Key
1. Visit [**NewsAPI.org**](https://newsapi.org)
2. Sign up for a free account
3. Go to the **Dashboard**
4. Copy your **API key** and paste it below 👇
""")

news_api_key = st.sidebar.text_input("Enter your NewsAPI key:", type="password")

country_names = {
    "global": "🌍 Global (No country filter)",
    "us": "🇺🇸 United States",
    "gb": "🇬🇧 United Kingdom",
    "jp": "🇯🇵 Japan",
    "in": "🇮🇳 India",
}
country = st.sidebar.selectbox("🌎 Choose a country:", list(country_names.keys()), format_func=lambda x: country_names[x])

# ---- OpenAI API Settings ----
st.sidebar.header("🧠 OpenAI Settings")
st.sidebar.markdown("""
### 👉 How to get an OpenAI API Key
1. Visit [**OpenAI API Keys**](https://platform.openai.com/api-keys)
2. Log in or sign up
3. Click **Create new secret key**
4. Copy and paste it below 👇
""")

openai_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# ✅ 최신 방식: 클라이언트 생성
client = None
if openai_key:
    client = OpenAI(api_key=openai_key)

# ---- Main Controls ----
topic = st.text_input("Enter a topic (optional):", "AI")
use_gpt_summary = st.toggle("🧠 GPT 요약 추가", value=False)

# ---- Helper: Clean text ----
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"window\.open\(.*?\)", "", text)
    text = re.sub(r"\{.*?window\.open.*?\}", "", text)
    text = re.sub(r"onclick=.*?(;|\"|')", "", text)
    text = re.sub(r"javascript:.*?(;|\"|')", "", text)
    text = re.sub(r"return\s+false;?", "", text)
    text = re.sub(r"[,;:]*\s*\d+\s*[\);]*", "", text)
    text = re.sub(r"[\{\}\(\)\[\]\<\>\"']", "", text)
    text = re.sub(r"\[\+\d+\s*chars\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---- GPT Summarization ----
def summarize_with_gpt(text):
    if not client:
        return "⚠️ GPT API 키가 설정되지 않았습니다."
    if not text.strip():
        return "요약할 내용이 없습니다."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 뉴스 기사를 간결하게 요약하는 어시스턴트야."},
                {"role": "user", "content": f"다음 기사를 한국어로 간결히 요약해줘:\n\n{text}"}
            ],
            temperature=0.4,
            max_tokens=120
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"요약 중 오류 발생: {str(e)}"

# ---- Fetch and Display News ----
if st.button("🔍 Search News"):
    if not news_api_key:
        st.warning("🔑 NewsAPI 키를 입력해주세요.")
    else:
        with st.spinner("뉴스를 불러오는 중..."):
            base_url = "https://newsapi.org/v2/"
            if country == "global":
                url = f"{base_url}everything?q={topic}&language=en&apiKey={news_api_key}"
            else:
                url = f"{base_url}top-headlines?country={country}&q={topic}&apiKey={news_api_key}"

            response = requests.get(url)
            data = response.json()

            if data.get("status") != "ok":
                st.error("⚠️ 뉴스를 불러오지 못했습니다. API 키 또는 요청 형식을 확인해주세요.")
            else:
                articles = data.get("articles", [])
                if not articles:
                    st.info("표시할 뉴스가 없습니다.")
                else:
                    for a in articles:
                        st.markdown(f"### [{a.get('title')}]({a.get('url')})")
                        st.caption(f"🗞️ {a.get('source', {}).get('name', 'Unknown')} | 📅 {a.get('publishedAt', '')[:10]}")
                        
                        desc = clean_text(a.get("description") or a.get("content") or "")
                        st.write(desc)

                        if use_gpt_summary:
                            summary = summarize_with_gpt(desc)
                            st.info(f"**🧠 GPT 요약:** {summary}")

                        st.divider()
