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

# =============================
# 🧭 사이드바
# =============================
st.sidebar.markdown("### 🧩 API 키 설정 방법")

with st.sidebar.expander("📡 NewsAPI 설정 방법"):
    st.markdown("""
    1. [NewsAPI.org](https://newsapi.org) 접속  
    2. 무료 회원가입 후 API 키 발급  
    3. 아래 입력란에 붙여넣기  
    """)

with st.sidebar.expander("🤖 OpenAI API 설정 방법"):
    st.markdown("""
    1. [OpenAI Platform](https://platform.openai.com/account/api-keys) 접속  
    2. API Key 생성 후 복사  
    3. 아래 입력란에 붙여넣기  
    """)

# 입력란
news_api_key = st.sidebar.text_input("📡 NewsAPI 키 입력", type="password")
openai_api_key = st.sidebar.text_input("🤖 OpenAI API 키 입력", type="password")

# 요약 기능 On/Off
use_gpt = st.sidebar.toggle("🧠 GPT 요약 활성화", value=True)

# 국가 선택 (한국 제외 + global 추가)
countries = {
    "global": "🌐 Global (전 세계)",
    "us": "🇺🇸 미국",
    "gb": "🇬🇧 영국",
    "jp": "🇯🇵 일본",
    "fr": "🇫🇷 프랑스",
    "de": "🇩🇪 독일",
    "in": "🇮🇳 인도",
    "cn": "🇨🇳 중국",
}
country = st.sidebar.selectbox("🌍 국가 선택", options=countries.keys(), format_func=lambda x: countries[x])

# =============================
# 🔍 뉴스 검색어 입력창
# =============================
st.markdown("### 🔎 뉴스 키워드 검색")
keyword = st.text_input("검색할 키워드를 입력하세요 (예: AI, 경제, 기술, 전쟁 등)", placeholder="예: AI chatbot, economy, technology")

# =============================
# 🧠 GPT 요약 함수
# =============================
def summarize_with_gpt(text, client, max_retries=3):
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
            if "insufficient_quota" in err_str or "quota" in err_str:
                return "⚠️ 요약 불가: OpenAI API 사용 한도가 초과되었습니다."
            if "rate" in err_str or "429" in err_str:
                if attempt < max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    return "⚠️ 요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
            print("GPT 요약 에러:", traceback.format_exc())
            return "⚠️ 요약 중 오류가 발생했습니다."

    return "⚠️ 요약 실패."


# =============================
# 📰 뉴스 데이터 가져오기
# =============================
@st.cache_data(show_spinner=False)
def get_news(api_key, country_code, keyword=None, page=1, page_size=5):
    endpoint = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "pageSize": page_size,
        "page": page,
    }

    # 글로벌 옵션일 때 country 제외
    if country_code != "global":
        params["country"] = country_code

    # 검색어 있으면 추가
    if keyword:
        params["q"] = keyword

    res = requests.get(endpoint, params=params)
    data = res.json()
    return data.get("articles", [])


# =============================
# 🚀 실행 부분
# =============================
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    client = None

if not news_api_key:
    st.warning("📡 NewsAPI 키를 왼쪽 입력창에 입력해주세요.")
else:
    # 현재 페이지 상태 관리 (Streamlit session_state 사용)
    if "page" not in st.session_state:
        st.session_state.page = 1

    # 데이터 불러오기
    articles = get_news(news_api_key, country, keyword, page=st.session_state.page)

    if not articles:
        if keyword:
            st.warning(f"'{keyword}' 관련 뉴스를 찾을 수 없습니다.")
        else:
            st.warning("뉴스를 불러올 수 없습니다. API 키 또는 국가 설정을 확인하세요.")
    else:
        for idx, article in enumerate(articles, 1):
            title = article.get("title", "제목 없음")
            desc = article.get("description", "내용 없음")
            url = article.get("url", "")
            img = article.get("urlToImage", None)

            with st.container():
                st.subheader(f"{title}")
                if img:
                    st.image(img, use_container_width=True)
                st.markdown(desc)
                st.markdown(f"[🔗 기사 바로가기]({url})")

                if use_gpt and client:
                    summary_text = summarize_with_gpt(desc, client)
                    st.markdown(f"🧠 **GPT 요약:** {summary_text}")
                st.divider()

        # ✅ "더 많은 기사 보기" 버튼 추가
        if st.button("🔽 더 많은 기사 보기"):
            st.session_state.page += 1
            st.rerun()
