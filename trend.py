import streamlit as st
import requests
import re
import openai

# ---- GPT API 키 입력 (Streamlit secrets로 관리하는 걸 권장) ----
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

# ---- Helper: 텍스트 정리 함수 ----
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

# ---- GPT 요약 함수 ----
def summarize_with_gpt(text):
    if not openai.api_key:
        return "⚠️ GPT API 키가 설정되지 않았습니다."
    if not text.strip():
        return "요약할 내용이 없습니다."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 뉴스 기사를 간결하게 요약하는 어시스턴트야."},
                {"role": "user", "content": f"다음 기사를 한국어로 간결히 요약해줘:\n\n{text}"}
            ],
            temperature=0.4,
            max_tokens=120
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return f"요약 중 오류 발생: {str(e)}"

# ---- Streamlit UI ----
st.title("📰 Global Trend News Dashboard")

api_key = st.text_input("🔑 NewsAPI Key", type="password")
country = st.selectbox("🌍 Choose a country", ["global", "us", "gb", "jp", "in"])
topic = st.text_input("Enter a topic (optional):", "AI")

# ✅ GPT 요약 기능 토글 버튼
use_gpt_summary = st.toggle("🧠 GPT 요약 추가", value=False)

if st.button("Search"):
    if not api_key:
        st.warning("API 키를 입력해주세요.")
    else:
        with st.spinner("뉴스를 불러오는 중..."):
            base_url = "https://newsapi.org/v2/"
            if country == "global":
                url = f"{base_url}everything?q={topic}&language=en&apiKey={api_key}"
            else:
                url = f"{base_url}top-headlines?country={country}&q={topic}&apiKey={api_key}"
            
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

                        # ✅ GPT 요약문 추가 (토글 ON일 때만)
                        if use_gpt_summary:
                            summary = summarize_with_gpt(desc)
                            st.info(f"**🧠 GPT 요약:** {summary}")
                        
                        st.divider()
