import streamlit as st
import requests
import re
import time
import traceback
from openai import OpenAI

# =============================
# ⚙️ 기본 설정
# =============================
st.set_page_config(page_title="AI 뉴스 요약", layout="wide")

st.title("📰 글로벌 트렌드 뉴스 요약 (GPT 요약 기능 포함)")

# OpenAI API 키 입력
api_key = st.sidebar.text_input("🔑 OpenAI API 키 입력", type="password")
use_gpt = st.sidebar.toggle("🧠 GPT 요약 활성화", value=True)

# 국가 선택 (한국 제외)
countries = {
    "us": "🇺🇸 미국",
    "jp": "🇯🇵 일본",
    "cn": "🇨🇳 중국",
    "gb": "🇬🇧 영국",
    "fr": "🇫🇷 프랑스",
    "de": "🇩🇪 독일",
}
country = st.sidebar.selectbox("🌍 국가 선택", options=countries.keys(), format_func=lambda x: countries[x])

# 뉴스 API 키
NEWS_API_KEY = "YOUR_NEWSAPI_KEY_HERE"  # 여기에 실제 News API 키 입력
NEWS_ENDPOINT = "https://newsapi.org/v2/top-headlines"


# =============================
# 🧠 GPT 요약 함수
# =============================
def summarize_with_gpt(text, client, max_retries=3):
    """GPT 요약 안전 버전: 재시도, 쿼터/인코딩 오류 처리"""
    if not client:
        return "⚠️ GPT API 키가 설정되지 않았습니다."
    if not text or not text.strip():
        return "요약할 내용이 없습니다."

    safe_text = re.sub(r"[^\x00-\x7F]+", " ", text).strip()
    backoff = 1

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 뉴스를 간결하게 요약하는 어시스턴트야."},
                    {"role": "user", "content": f"다음 기사를 한국어로 2~3문장으로 요약해줘:\n\n{safe_text}"}
                ],
                temperature=0.4,
                max_tokens=120
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            err_str = str(e).lower()

            # ✅ 쿼터 부족 (결제 문제)
            if "insufficient_quota" in err_str or "quota" in err_str:
                return "⚠️ 요약 불가: OpenAI API 사용 한도가 초과되었습니다. Billing(결제)을 확인해주세요."

            # ✅ 과도한 요청 (429)
            if "rate" in err_str or "429" in err_str:
                if attempt < max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    return "⚠️ 요청이 너무 많습니다. 잠시 후 다시 시도해주세요."

            # ✅ 그 외 오류
            print("GPT 요약 에러:", traceback.format_exc())
            return "⚠️ 요약 중 오류가 발생했습니다."

    return "⚠️ 요약 실패."


# =============================
# 📰 뉴스 데이터 가져오기
# =============================
@st.cache_data(show_spinner=False)
def get_news(country_code):
    params = {
        "country": country_code,
        "apiKey": NEWS_API_KEY,
        "pageSize": 5,  # 기사 수 조정
    }
    res = requests.get(NEWS_ENDPOINT, params=params)
    data = res.json()
    return data.get("articles", [])


# =============================
# 🚀 실행 부분
# =============================
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

articles = get_news(country)

if not articles:
    st.warning("뉴스를 불러올 수 없습니다. API 키 또는 국가 설정을 확인하세요.")
else:
    for idx, article in enumerate(articles, 1):
        title = article.get("title", "제목 없음")
        desc = article.get("description", "내용 없음")
        url = article.get("url", "")
        img = article.get("urlToImage", None)

        with st.container():
            st.subheader(f"{idx}. {title}")
            if img:
                st.image(img, use_container_width=True)
            st.markdown(desc)
            st.markdown(f"[🔗 기사 바로가기]({url})")

            # ✅ GPT 요약 표시 (토글이 켜져 있을 때만)
            if use_gpt and client:
                summary_text = summarize_with_gpt(desc, client)
                st.markdown(f"🧠 **GPT 요약:** {summary_text}")
            st.divider()
