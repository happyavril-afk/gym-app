import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import io
import time
from datetime import datetime
import google.generativeai as genai

# ==========================================
# 0. 🤖 Gemini AI 자동 설정
# ==========================================
if 'gemini_api_key' not in st.session_state:
    try:
        st.session_state['gemini_api_key'] = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.session_state['gemini_api_key'] = ""

@st.cache_data(ttl=3600) 
def get_ai_greeting(user_name, routine_theme, api_key):
    if not api_key or len(api_key) < 10: 
        return f"🗣 (기본 모드) '{user_name}님, 오늘의 테마는 [{routine_theme}]입니다! 부상 없이 파이팅해봐요!'"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"너는 친절하고 전문적인 헬스장 AI 트레이너야. 회원이름은 '{user_name}'이고, 오늘 운동 테마는 '{routine_theme}'야. 이 회원에게 오늘 이 테마를 추천하는 이유를 살짝 섞어서, 파이팅 넘치고 경쾌한 코칭 멘트 2~3문장을 작성해줘. 이모지도 적절히 써줘."
        response = model.generate_content(prompt)
        return f"🗣 AI 트레이너: '{response.text.strip()}'"
    except:
        return f"🗣 (시스템) '{user_name}님, 오늘도 파이팅입니다! 준비된 루틴을 시작해볼까요?'"

@st.cache_data(ttl=3600)
def get_ai_workout_feedback(user_name, planned_count, completed_count, total_sets, total_vol, cardio_time, api_key):
    if not api_key or len(api_key) < 10: 
        return f"🗣 (기본 모드) '{user_name}님, 오늘 계획한 {planned_count}개 중 {completed_count}개를 마쳤어요! 총 {total_vol}kg 볼륨을 달성하셨네요. 다음엔 상체부터 시작해볼까요?'"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"너는 철저하게 사실 기반으로만 말하는 AI 트레이너야. '{user_name}' 회원이 오늘 계획된 루틴 {planned_count}개 중 {completed_count}개를 완료했어. "
                  f"(오늘 달성 수치 -> 총 웨이트 세트: {total_sets}세트, 웨이트 볼륨: {total_vol}kg, 유산소: {cardio_time}). "
                  f"다음 4가지 규칙을 무조건 지켜서 3문장 이내로 작성해."
                  f"1. 시작은 반드시 '오늘 계획한 {planned_count}개 중 {completed_count}개를 마쳤어요'라는 문장으로 시작할 것."
                  f"2. 위에서 주어진 '오늘 달성 수치'만을 인용하여 철저하게 [관찰값] 기반의 칭찬만 할 것. 거짓으로 과거와 비교하지 말 것."
                  f"3. 절대 칼로리 소모량, 근력 향상, 체형 변화 등 측정되지 않은 값이나 의학적/추측성 멘트는 금지할 것."
                  f"4. 마지막 문장은 '다음에는 상체(또는 다른 부위) 운동부터 시작해 볼까요?' 처럼 다음 방문을 제안하며 끝낼 것.")
        response = model.generate_content(prompt)
        return f"🗣 AI 트레이너: '{response.text.strip()}'"
    except:
        return f"🗣 (시스템) '{user_name}님, 오늘 계획한 {planned_count}개 중 {completed_count}개를 마쳤어요!'"

@st.cache_data(ttl=3600)
def get_ai_monthly_feedback(user_name, total_days, prev_days, freq_part, api_key):
    if not api_key or len(api_key) < 10: 
        return f"🗣 (기본 모드) '{user_name}님, 이번 달에는 총 {total_days}일 운동했고 지난달보다 {total_days - prev_days}일 늘었어요. {freq_part} 운동은 꾸준했네요. 다음 달에는 상체 운동을 주 1회 추가해 볼까요?'"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"너는 AI 트레이너야. '{user_name}' 회원의 월간 운동 리포트를 요약해줘. "
                  f"총 운동일: {total_days}일 (지난달: {prev_days}일), 자주 한 부위: {freq_part}. "
                  f"1. 반드시 '이번 달에는 총 {total_days}일 운동했고 지난달보다 {total_days - prev_days}일 늘었어요.'라는 문장으로 시작해. "
                  f"2. {freq_part} 운동의 꾸준함을 칭찬하고, 상대적으로 부족했던 부위의 운동을 다음 달 행동으로 제안해. "
                  f"3. 3문장 이내로 작성하고 의학적 판단은 배제해.")
        response = model.generate_content(prompt)
        return f"🗣 AI 트레이너: '{response.text.strip()}'"
    except:
        return f"🗣 (시스템) '이번 달 총 {total_days}일 운동 완료! 훌륭합니다.'"

# ==========================================
# 1. 🌐 구글 스프레드시트 (CSV) 연동 설정
# ==========================================
SHEET_ID = "1Kf_FrZIoagIXkZIH1dO14fKPpgbLk85qDDM_r4zfno8"
SHEET_URL_MEMBER_ANALYTICS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
SHEET_URL_WORKOUT_HISTORY  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=991554144" 
SHEET_URL_HEATMAP          = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=347441251" 
SHEET_URL_QNA              = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=522963216" 
SHEET_URL_FACILITY         = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=808495575" 

FALLBACK_DATA = {
    "member": "회원명,가입일,잔여일,주평균방문,방문추세,볼륨증감률(%),정체종목,정체기간(주),이탈확률(%),타겟분류\n김철수,2025.11.15,45,1.2,감소 📉,-15,없음,0,88,이탈위험\n박지민,2026.01.10,120,1.5,감소 📉,-10,없음,0,75,이탈위험\n이광수,2024.05.10,150,4.5,증가 📈,12,없음,0,5,VIP\n송지효,2023.11.22,210,5.1,증가 📈,22,없음,0,2,VIP\n최운식,2025.05.15,180,3.0,유지 ➖,2,스쿼트,4,25,정체기\n전소민,2026.02.28,60,2.5,유지 ➖,0,숄더 프레스,3,40,정체기",
    "workout": "날짜,회원명,운동 부위,주요 기구,중량(kg),횟수,세트,총 볼륨(kg)\n07.01,박수민,등,랫풀다운,15,12,5,900\n07.02,이광수,등,케이블 로우,45,15,3,2025\n07.03,마동석,하체,레그 익스텐션,140,12,3,5040\n07.03,박수민,가슴,체스트 프레스,40,15,3,1800\n07.04,박수민,가슴,벤치프레스,40,10,4,1600",
    "heatmap": "시간,파워 랙 (웨이트),트레드밀 (유산소),스미스 머신,스트레칭존,케이블 머신\n06:00,10,25,5,15,10\n09:00,25,45,15,20,25\n12:00,30,35,25,25,40\n15:00,50,60,40,30,55\n18:00,95,100,85,60,90",
    "qna": "id,시간,회원명,유형,내용,상태,답변\n1,오늘 14:20,박수민,🏋 운동/자세 피드백,어깨가 결려요.,대기중,\n2,오늘 13:05,김민지,💳 회원권/PT 문의,할인 문의,답변완료,적용됩니다!",
    "facility": "id,시간,신고자,위치,내용,상태,답변\n1,오늘 09:15,이동국,프리웨이트존,조절 핀 불량,접수됨,\n2,어제 21:00,유재석,남자 탈의실,수압이 약해요,조치중,수리 요청함"
}

@st.cache_data(ttl=600)  
def fetch_data(url, fallback_key, required_col=None):
    try:
        df = pd.read_csv(url)
        if not df.empty and len(df.columns) > 0 and '<html' not in str(df.columns[0]).lower():
            if len(df.columns) == 1 and ',' in df.columns[0]:
                col_name = df.columns[0]
                raw_text = col_name + '\n' + '\n'.join(df[col_name].astype(str).tolist())
                df = pd.read_csv(io.StringIO(raw_text))
            df.columns = df.columns.str.strip()
            df = df.dropna(how='all')
            if '티겟분류' in df.columns: df.rename(columns={'티겟분류': '타겟분류'}, inplace=True)
            if not required_col or required_col in df.columns: 
                return df
    except:
        pass
    fallback_df = pd.read_csv(io.StringIO(FALLBACK_DATA.get(fallback_key, "")))
    fallback_df.columns = fallback_df.columns.str.strip()
    return fallback_df

df_members = fetch_data(SHEET_URL_MEMBER_ANALYTICS, "member", "회원명")
history_df = fetch_data(SHEET_URL_WORKOUT_HISTORY, "workout", "날짜")
heatmap_df = fetch_data(SHEET_URL_HEATMAP, "heatmap", "시간")
df_qna_init = fetch_data(SHEET_URL_QNA, "qna").fillna("")
df_fac_init = fetch_data(SHEET_URL_FACILITY, "facility").fillna("")

if '타겟분류' in df_members.columns:
    churn_df = df_members[df_members['타겟분류'] == '이탈위험'].drop(columns=['타겟분류', '정체종목', '정체기간(주)'], errors='ignore')
    vip_df = df_members[df_members['타겟분류'] == 'VIP'].drop(columns=['타겟분류', '정체종목', '정체기간(주)', '이탈확률(%)'], errors='ignore')
    sales_df = df_members[df_members['타겟분류'] == '정체기'].drop(columns=['타겟분류', '잔여일', '이탈확률(%)'], errors='ignore')
else:
    churn_df, vip_df, sales_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# ==========================================
# 2. 페이지 및 세션 상태 초기화
# ==========================================
st.set_page_config(page_title="FITPASS PRO", page_icon="⚡", layout="wide")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'role' not in st.session_state: st.session_state['role'] = None
if 'qna_db' not in st.session_state: st.session_state['qna_db'] = df_qna_init.to_dict('records')
if 'facility_db' not in st.session_state: st.session_state['facility_db'] = df_fac_init.to_dict('records')
if 'current_user' not in st.session_state: st.session_state['current_user'] = "박수민"
if 'workout_state' not in st.session_state: st.session_state['workout_state'] = "준비" 
if 'ai_mode' not in st.session_state: st.session_state['ai_mode'] = True 
if 'today_records' not in st.session_state: st.session_state['today_records'] = []

if 'reminders_on' not in st.session_state: st.session_state['reminders_on'] = True 
if 'next_workout_promise' not in st.session_state: st.session_state['next_workout_promise'] = None 
if 'next_workout_repeat' not in st.session_state: st.session_state['next_workout_repeat'] = "" 

if 'fav_machines' not in st.session_state: st.session_state['fav_machines'] = ["파워 랙 (스쿼트)"] 
if 'coins' not in st.session_state: st.session_state['coins'] = 1200 
if 'coin_history' not in st.session_state:
    st.session_state['coin_history'] = [
        {"날짜": "2026.09.28", "내용": "주간 목표 달성", "변동": "+500", "잔액": 1200},
        {"날짜": "2026.09.25", "내용": "단백질 쉐이크 교환", "변동": "-300", "잔액": 700},
        {"날짜": "2026.09.20", "내용": "가입 축하금", "변동": "+1000", "잔액": 1000}
    ]

ROUTINE_DB = {
    "박수민": {
        "theme": "🔥 하체 볼륨업 (근력 증가)",
        "reason": "최근 2주간 상체 대비 하체 운동 빈도가 약 20% 부족했습니다. 오늘은 하체 볼륨을 확실히 채워 신체 밸런스를 맞추는 것을 권장합니다.",
        "routines": [
            {"id": 0, "부위": "워밍업", "기구": "트레드밀", "목표": "속도 6.0 가볍게 걷기", "시간": "10분", "완료": False, "상태": "대기"},
            {"id": 1, "부위": "하체", "기구": "파워 랙 (스쿼트)", "목표": "80kg x 10회 (4세트)", "시간": "15분", "완료": False, "상태": "대기"},
            {"id": 2, "부위": "하체", "기구": "레그 프레스", "목표": "120kg x 12회 (3세트)", "시간": "12분", "완료": False, "상태": "대기"}
        ]
    },
    "최운식": {
        "theme": "💪 정체기 돌파 가슴 루틴",
        "reason": "최근 벤치프레스 중량(75kg)이 3주째 정체되어 있습니다. 오늘은 인클라인과 덤벨 위주로 자극점을 바꿔 근신경계를 깨워보겠습니다.",
        "routines": [
            {"id": 0, "부위": "워밍업", "기구": "사이클", "목표": "강도 3 가볍게 페달링", "시간": "10분", "완료": False, "상태": "대기"},
            {"id": 1, "부위": "가슴", "기구": "벤치프레스 머신", "목표": "70kg x 12회 (4세트) - 하향", "시간": "15분", "완료": False, "상태": "대기"},
            {"id": 2, "부위": "가슴", "기구": "인클라인 벤치", "목표": "50kg x 12회 (3세트)", "시간": "12분", "완료": False, "상태": "대기"}
        ]
    },
    "default": {
        "theme": "🏃 전신 순환 및 밸런스",
        "reason": "최근 운동 이력이 충분하지 않아, 오늘은 전신을 골고루 자극하며 기초 체력을 기르는 안전한 루틴을 구성했습니다.",
        "routines": [
            {"id": 0, "부위": "워밍업", "기구": "트레드밀 (유산소)", "목표": "속도 5.5", "시간": "10분", "완료": False, "상태": "대기"},
            {"id": 1, "부위": "가슴", "기구": "벤치프레스 머신", "목표": "20kg x 15회 (3세트)", "시간": "10분", "완료": False, "상태": "대기"},
            {"id": 2, "부위": "등", "기구": "랫풀다운", "목표": "20kg x 15회 (3세트)", "시간": "10분", "완료": False, "상태": "대기"}
        ]
    }
}

MACHINE_INSTRUCTIONS = {
    "파워 랙 (스쿼트)": {
        "img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470",
        "target": "주요 부위: 대퇴사두근, 둔근 (하체 전체)",
        "steps": ["1️⃣ [조절] 바벨 높이를 본인의 어깨선에 맞게 세팅합니다.", "2️⃣ [시작] 바벨을 승모근에 단단히 얹고 가슴을 폅니다.", "3️⃣ [움직임] 엉덩이를 뒤로 빼며 무릎이 발끝 방향을 향하도록 앉았다 일어납니다.", "4️⃣ [종료] 완전히 일어선 후 안전바 위치를 확인하며 바벨 거치."]
    },
    "벤치프레스 머신": {
        "img": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=1470",
        "target": "주요 부위: 대흉근, 삼두근 (가슴/팔)",
        "steps": ["1️⃣ [조절] 등받이와 안장 높이를 조절하여 그립이 가슴 중앙에 오도록 합니다.", "2️⃣ [시작] 엉덩이와 등을 패드에 밀착하고 손잡이를 단단히 잡습니다.", "3️⃣ [움직임] 가슴 근육의 수축을 느끼며 밀어낸 후 천천히 저항하며 돌아옵니다.", "4️⃣ [종료] 무게추가 완전히 닿기 전에 멈추고 안전하게 손잡이를 놓습니다."]
    },
    "랫풀다운": {
        "img": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=1470",
        "target": "주요 부위: 광배근, 이두근 (등/팔)",
        "steps": ["1️⃣ [조절] 허벅지가 뜨지 않도록 고정 패드를 본인 체형에 맞게 낮춰 조절합니다.", "2️⃣ [시작] 어깨너비보다 넓게 바를 잡고 앉아 허리를 곧게 폅니다.", "3️⃣ [움직임] 가슴을 열고 쇄골 쪽으로 바를 당긴 후, 광배근 자극을 느끼며 올립니다.", "4️⃣ [종료] 팔을 완전히 펴기 전 통제하며 동작을 마무리합니다."]
    },
    "트레드밀": {
        "img": "https://images.unsplash.com/photo-1538805060514-97d9cc17730c?q=80&w=1470",
        "target": "주요 부위: 전신 유산소 및 심폐지구력",
        "steps": ["1️⃣ [조절] 안전을 위해 비상 정지 핀을 옷에 고정합니다.", "2️⃣ [시작] 양옆 고정 발판에 선 상태로 디스플레이의 시작 버튼을 누릅니다.", "3️⃣ [움직임] 벨트가 움직이기 시작하면 속도와 경사도를 서서히 올리며 바른 자세로 걷거나 뜁니다.", "4️⃣ [종료] 정지 버튼을 누르고 벨트가 완전히 멈춘 것을 확인한 후 내려옵니다."]
    }
}

def reset_routine(user_name):
    import copy
    db_entry = ROUTINE_DB.get(user_name, ROUTINE_DB.get("박수민"))
    st.session_state['routine_theme'] = db_entry["theme"]
    st.session_state['routine_reason'] = db_entry["reason"]
    st.session_state['my_routine'] = copy.deepcopy(db_entry["routines"])

if 'my_routine' not in st.session_state: reset_routine(st.session_state['current_user'])

# ==========================================
# 3. 🎨 커스텀 CSS (UI 개선 완벽 적용)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    @font-face { font-family: 'GmarketSans'; src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); font-weight: 500; }
    @font-face { font-family: 'GmarketSans'; src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff') format('woff'); font-weight: 700; }
    p, h1, h2, h3, h4, h5, h6, label, li, a, button, svg text, canvas { font-family: 'GmarketSans', 'Montserrat', sans-serif !important; letter-spacing: -0.5px; }
    [data-testid="stDataFrame"] div, [data-testid="stTable"] th, [data-testid="stTable"] td { font-family: 'GmarketSans', sans-serif !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #1e293b !important; }
    
    .reward-card { background: rgba(255, 255, 255, 0.05); border: 1px solid #4facfe; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; }
    .coin-text { font-size: 1.5rem; font-weight: bold; color: #ccff00; }
    .badge-card { text-align:center; padding:15px; background:#1e293b; border-radius:12px; border:2px solid #ccff00; margin-bottom:10px; }
    .badge-card-locked { text-align:center; padding:15px; background:#0f172a; border-radius:12px; opacity:0.4; margin-bottom:10px; }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state['logged_in']:
        st.markdown("""
        <style>
        .stApp { background-image: linear-gradient(rgba(10,10,12,0.6), rgba(10,10,12,0.8)), url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070'); background-size: cover; background-position: center; }
        .hero-title { font-family: 'Montserrat', sans-serif !important; font-size: clamp(4rem, 10vw, 8rem) !important; font-weight: 900; color: #ffffff; text-align: center; margin-top: 15vh; text-shadow: 0 4px 20px rgba(0,0,0,0.8); }
        .hero-subtitle { font-size: clamp(1.5rem, 4vw, 2.5rem) !important; color: #ccff00; text-align: center; font-weight: 700; margin-bottom: 80px; text-shadow: 0 2px 10px rgba(0,0,0,0.8); }
        .stButton>button { border-radius: 20px !important; font-size: clamp(1.5rem, 3vw, 2.5rem) !important; font-weight: 900 !important; padding: 2rem 1rem !important; border: 3px solid #ccff00 !important; color: #ccff00 !important; background: rgba(0, 0, 0, 0.7) !important; backdrop-filter: blur(10px); height: auto !important; transition: all 0.3s ease !important; }
        .stButton>button:hover { transform: scale(1.03); box-shadow: 0 0 20px rgba(204,255,0,0.6) !important; color: #ccff00 !important; }
        </style>
        """, unsafe_allow_html=True)

    elif st.session_state['role'] == 'MEMBER':
        st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; }
        [data-testid="stMain"] p, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4, [data-testid="stMain"] label, [data-testid="stMain"] li, [data-testid="stMain"] b, [data-testid="stMain"] strong, [data-testid="stMain"] span:not([class*="stIcon"]):not(.material-icons) { color: #ffffff !important; }
        
        /* 🔥 [UI 개선 1] 하얀색 입력 박스(파일업로드, 셀렉트박스 등) 내부 글자를 어두운 네이비색으로 고정하여 시인성 100% 확보 */
        [data-baseweb="select"] span, 
        [data-baseweb="select"] div,
        [data-baseweb="input"] input, 
        [data-testid="stFileUploadDropzone"] p,
        [data-testid="stFileUploadDropzone"] span,
        [data-testid="stFileUploadDropzone"] small,
        [data-testid="stFileUploadDropzone"] svg { color: #0f172a !important; fill: #0f172a !important; font-weight: 600 !important; }

        .insta-gradient-text { font-family: 'Montserrat', sans-serif !important; background: linear-gradient(to right, #00f2fe, #4facfe) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-weight: 900 !important; font-size: 2.5rem !important; text-align: center !important; }
        .profile-card { background: rgba(255, 255, 255, 0.1) !important; border-radius: 24px !important; padding: 20px !important; margin-bottom: 20px !important; color: #ffffff !important;}
        .owoonwan-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid #4facfe; border-radius: 15px; padding: 30px; text-align: center; color: white; margin-top: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
        
        /* 🔥 [UI 개선 2] 버튼 Hover 시 색상 변경 대신, 크기 확대(Scale) 및 파란 네온 글로우 효과 적용 */
        button[kind="primary"] { background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important; color: #111111 !important; border: none !important; border-radius: 12px !important; font-weight: 800 !important; transition: all 0.3s ease !important; }
        button[kind="primary"]:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 242, 254, 0.6) !important; color: #111111 !important; }
        
        button[kind="secondary"] { background-color: rgba(255,255,255,0.05) !important; color: #ffffff !important; border: 1px solid #4facfe !important; border-radius: 12px !important; font-weight: 600 !important; transition: all 0.3s ease !important; }
        button[kind="secondary"]:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(255, 255, 255, 0.3) !important; background-color: rgba(255, 255, 255, 0.1) !important; border-color: #00f2fe !important; color: #ffffff !important; }
        </style>
        """, unsafe_allow_html=True)
        
    elif st.session_state['role'] == 'OWNER':
        st.markdown("""
        <style>
        .stApp { background-color: #F4F7F9 !important; }
        [data-testid="stMain"] p, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4, [data-testid="stMain"] span, [data-testid="stMain"] label { color: #1e293b !important; }
        .corp-card { background-color: #ffffff !important; border-radius: 12px; padding: 20px; border-left: 5px solid #2563EB; margin-bottom: 20px; color: #1e293b !important;}
        
        /* 점주 화면 버튼 Hover 애니메이션 통일 */
        button[kind="primary"] { background-color: #2563EB !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: 700 !important; transition: all 0.3s ease !important; }
        button[kind="primary"]:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important; color: #ffffff !important; }
        
        button[kind="secondary"] { background-color: #ffffff !important; color: #1e293b !important; border-radius: 8px !important; border: 1px solid #cbd5e1 !important; font-weight: 600 !important; transition: all 0.3s ease !important; }
        button[kind="secondary"]:hover { transform: scale(1.02); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1) !important; background-color: #eff6ff !important; border-color: #2563EB !important; color: #1e293b !important; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 4. 📱 회원 (MEMBER) 앱 화면
# ==========================================
def member_app():
    st.sidebar.markdown("**👟 회원 (B2C) 제어판**")
    
    all_members = df_members['회원명'].tolist() if not df_members.empty else ["박수민", "최운식"]
    if "박수민" not in all_members: all_members.insert(0, "박수민")
    
    idx = all_members.index(st.session_state['current_user']) if st.session_state['current_user'] in all_members else 0
    selected_user = st.sidebar.selectbox("👤 데모 회원 전환", all_members, index=idx)
    
    if selected_user != st.session_state['current_user']:
        st.session_state['current_user'] = selected_user
        st.session_state['workout_state'] = "준비"
        st.session_state['today_records'] = []
        reset_routine(selected_user)
        st.rerun()

    current_user_name = st.session_state['current_user']
    
    if st.session_state['workout_state'] == "진행중":
        if st.sidebar.button("🏁 오늘 운동 마치기", type="primary"):
            st.session_state['workout_state'] = "완료"
            st.rerun()

    menu = st.sidebar.radio("📋 메뉴 선택", [
        "📊 1. 인바디 및 목표 설정",
        "🚀 2. 오늘의 처방 (AI 루틴)", 
        "📡 3. 기구 스캔 (기록/타이머)", 
        "📈 4. 리포트 및 오운완(종료)", 
        "🏆 5. 랭킹 및 리워드",
        "💬 6. 소통 및 설정함"
    ])

    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<div class='insta-gradient-text'>FITPASS PRO</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-card'><b style='color:#ffffff;'>@{current_user_name}_workout</b>님, 환영합니다!<br><span style='color:#00f2fe !important;'>운동 상태: {st.session_state['workout_state']}</span></div>", unsafe_allow_html=True)
        
        if st.session_state.get('next_workout_promise') and st.session_state.get('reminders_on', True):
            c_banner1, c_banner2 = st.columns([4, 1])
            with c_banner1:
                st.info(f"🔔 **AI 리마인드:** {st.session_state['next_workout_promise']}에 운동 예약됨 {st.session_state['next_workout_repeat']}")
            with c_banner2:
                if st.button("예약 취소", key="cancel_promise"):
                    st.session_state['next_workout_promise'] = None
                    st.toast("운동 약속이 취소되었습니다.")
                    st.rerun()

        if menu == "📊 1. 인바디 및 목표 설정":
            st.markdown("### 📊 M02. 인바디 업로드 및 분석")
            uploaded_file = st.file_uploader("인바디 결과지 (이미지/PDF) 업로드")
            if uploaded_file is not None:
                with st.spinner("AI가 체성분 데이터를 분석 중입니다..."): time.sleep(1.5)
                st.success(f"✅ 측정일 ({datetime.now().strftime('%Y-%m-%d')}) 데이터 인식 완료!")
                st.info("💡 **AI 분석 요약 (의료진단 배제)**\n\n골격근량 대비 체지방률이 다소 높습니다. 질병 진단이 아니며, 근력 강화를 위해 오늘은 하체 위주의 볼륨 트레이닝을 권장합니다.")
            
            st.selectbox("🎯 최우선 운동 목표", ["근력 증가 (벌크업)", "체중 관리 (다이어트)", "운동 습관 만들기"])
            st.number_input("주당 희망 방문 횟수", min_value=1, max_value=7, value=4)
            avoid = st.multiselect("피하고 싶은 부위 (부상 등)", ["어깨", "허리", "무릎", "손목"])
            if avoid: st.warning(f"⚠️ '{', '.join(avoid)}' 부위에 무리가 가는 기구는 추천에서 제외하고 대체 운동을 제안합니다.")
            
            if st.button("목표 저장", use_container_width=True): st.toast("목표 저장 완료!")

        elif menu == "🚀 2. 오늘의 처방 (AI 루틴)":
            st.markdown("### 🤖 M03. AI 트레이너 추천 루틴")
            
            if not st.session_state.get('ai_mode', True):
                st.warning("⚠️ 현재 '기본 모드(AI 개인화 중지)' 상태입니다. 기구 스캔 탭에서 직접 운동을 선택해 진행해주세요.")
            else:
                db_entry = ROUTINE_DB.get(current_user_name, ROUTINE_DB["default"])
                theme = db_entry["theme"]
                reason = db_entry["reason"]
                
                ai_msg = get_ai_greeting(current_user_name, theme, st.session_state['gemini_api_key'])
                st.success(ai_msg)
                
                st.markdown(f"#### 🎯 오늘의 추천 테마: **{theme}**")
                st.info(f"💡 **AI 추천 근거:** {reason}")
                
                st.write("---")
                
                completed_count = sum(1 for r in st.session_state['my_routine'] if r.get('완료', False))
                st.progress(completed_count / len(st.session_state['my_routine']), text=f"루틴 진행률: {completed_count} / {len(st.session_state['my_routine'])} 완료")
                
                for idx, r in enumerate(st.session_state['my_routine']):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        status_mark = "✅" if r.get('완료', False) else ("⏭️" if r.get('상태', '대기') == "건너뜀" else "⬜")
                        st.markdown(f"**{status_mark} [{r.get('부위', '')}] {r.get('기구', '')}**")
                        st.caption(f"🔹 목표: {r.get('목표', '')} | ⏱️ 예상 소요: {r.get('시간', '10분')}")
                    with col2:
                        if not r.get('완료', False) and r.get('상태', '대기') != "건너뜀":
                            if st.button("건너뛰기/변경", key=f"rep_{idx}"):
                                st.session_state[f"show_exp_{idx}"] = not st.session_state.get(f"show_exp_{idx}", False)
                                st.rerun()

                    if st.session_state.get(f"show_exp_{idx}", False) and not r.get('완료', False):
                        with st.container():
                            reason_skip = st.selectbox("건너뛰는 사유를 알려주세요", ["기구 사용 중(대기 김)", "컨디션 저하/통증", "다른 운동으로 대체"], key=f"rsn_{idx}")
                            if st.button("적용하기", key=f"apply_{idx}"):
                                st.session_state['my_routine'][idx]['상태'] = "건너뜀"
                                st.session_state[f"show_exp_{idx}"] = False
                                st.toast("해당 루틴이 '건너뜀' 처리되었습니다.")
                                st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.session_state['workout_state'] == "준비":
                    if st.button("💪 운동 시작하기", type="primary", use_container_width=True): 
                        st.session_state['workout_state'] = "진행중"
                        st.toast("🔥 운동 세션이 시작되었습니다! 기구 스캔 탭으로 이동하세요.")
                        st.rerun()
                elif st.session_state['workout_state'] == "진행중":
                    st.info("🏃 현재 운동이 진행 중입니다. 기록을 위해 '기구 스캔' 탭을 이용하세요.")

        elif menu == "📡 3. 기구 스캔 (기록/타이머)":
            st.markdown("### 📡 M06 & M25. 기구 스캔 및 즐겨찾기")
            
            selected_machine = None
            if st.session_state['fav_machines']:
                fav_sel = st.radio("⭐ 즐겨찾기 기구 빠른 선택 (M25):", ["선택 안 함"] + st.session_state['fav_machines'], horizontal=True)
                if fav_sel != "선택 안 함":
                    selected_machine = fav_sel

            if not selected_machine:
                machine_options = ["📱 기구 대기 중...", "파워 랙 (스쿼트)", "벤치프레스 머신", "랫풀다운", "트레드밀 (유산소)"]
                machine_sel = st.selectbox("가상 NFC 태그 시뮬레이터:", machine_options)
                if machine_sel != "📱 기구 대기 중...":
                    selected_machine = machine_sel

            if selected_machine:
                is_fav = selected_machine in st.session_state['fav_machines']
                if st.toggle(f"⭐ '{selected_machine}' 즐겨찾기 설정", value=is_fav):
                    if selected_machine not in st.session_state['fav_machines']:
                        st.session_state['fav_machines'].append(selected_machine)
                else:
                    if selected_machine in st.session_state['fav_machines']:
                        st.session_state['fav_machines'].remove(selected_machine)

                search_keyword = selected_machine.split(" ")[0]
                if "트레드밀" in selected_machine: search_keyword = "트레드밀"
                
                m_info = MACHINE_INSTRUCTIONS.get(selected_machine) or MACHINE_INSTRUCTIONS.get(search_keyword)
                if m_info:
                    with st.expander(f"📖 [{selected_machine}] 사용 가이드 보기 (M07)", expanded=True):
                        st.image(m_info["img"], use_container_width=True)
                        st.markdown(f"**🎯 {m_info['target']}**")
                        for step in m_info["steps"]:
                            st.write(step)
                        st.warning("⚠️ **주의:** 통증이나 이상을 느끼면 즉시 운동을 중지하세요.")
                
                if "유산소" in selected_machine:
                    st.markdown("---")
                    st.markdown("#### 🏃 웨어러블 디바이스 연동 시연 중...")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("현재 심박수", "135 bpm")
                    c2.metric("경과 시간", "25:40")
                    c3.metric("소모 칼로리", "210 kcal")
                    if st.button("유산소 종료 및 저장", use_container_width=True): 
                        st.session_state['today_records'].append({"기구": search_keyword, "내용": "25분 40초 완료"})
                        st.toast("✅ 유산소 데이터가 저장되었습니다!")
                else:
                    st.markdown("---")
                    st.markdown("#### 📝 운동 기록 입력")
                    last_w, last_r = 20, 10 
                    if '회원명' in history_df.columns and not history_df[history_df['회원명'] == current_user_name].empty:
                        past = history_df[(history_df['회원명'] == current_user_name) & (history_df['주요 기구'].str.contains(search_keyword, na=False))]
                        if not past.empty:
                            last_record = past.sort_values(by="날짜", ascending=False).iloc[0]
                            last_w, last_r = int(last_record.get('중량(kg)', 20)), int(last_record.get('횟수', 10))
                            st.success(f"💡 **지난번 기록 적용:** {last_w}kg x {last_r}회 ({last_record.get('날짜', '')})")
                    
                    c1, c2 = st.columns(2)
                    with c1: weight = st.number_input("중량 (kg)", value=last_w, step=5)
                    with c2: reps = st.number_input("반복 횟수", value=last_r, step=1)
                    
                    st.markdown("#### 📊 현재 세트 기록 현황")
                    if st.session_state['today_records']:
                        df_today = pd.DataFrame(st.session_state['today_records'])
                        st.dataframe(df_today, use_container_width=True)
                        if st.button("🗑️ 마지막 기록 삭제"):
                            st.session_state['today_records'].pop()
                            st.rerun()
                    else:
                        st.caption("아직 기록된 세트가 없습니다.")
                    
                    if st.button("💪 현재 세트 기록 완료 및 휴식", type="primary", use_container_width=True): 
                        for r in st.session_state['my_routine']:
                            if search_keyword in r.get('기구', ''): r['완료'] = True
                        st.session_state['today_records'].append({"기구": selected_machine, "중량": weight, "횟수": reps})
                        st.toast(f"✅ {selected_machine} 세트 저장됨!")
                        
                        bar = st.progress(0, text="⏱️ 60초 휴식 타이머 진행 중...")
                        for p in range(100):
                            time.sleep(0.01) 
                            bar.progress(p + 1, text="⏱️ 60초 휴식 타이머 진행 중...")
                        st.info("🔔 휴식 종료! 다음 세트를 준비하세요.")
                        st.rerun()

        elif menu == "📈 4. 리포트 및 오운완(종료)":
            if st.session_state['workout_state'] == "진행중":
                st.markdown("### 🏁 M12. 오늘 운동 종료하기")
                st.warning("🏃 아직 운동 세션이 진행 중입니다. 최종 종료하시겠습니까?")
                
                planned_items = st.session_state['my_routine']
                st.markdown("#### 📋 현재까지 수행 내역 요약")
                for r in planned_items:
                    if r.get('완료', False):
                        st.write(f"✅ **{r.get('기구')}** - 완료")
                    elif r.get('상태') == '건너뜀':
                        st.write(f"⏭️ **{r.get('기구')}** - 건너뜀")
                    else:
                        st.write(f"⬜ **{r.get('기구')}** - 미완료")
                
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💪 계속 운동하기", use_container_width=True):
                        st.toast("기구 스캔 탭으로 이동해주세요.")
                with col2:
                    if st.button("🚨 최종 종료하고 리포트 보기", type="primary", use_container_width=True):
                        st.session_state['workout_state'] = "완료"
                        st.session_state['coins'] += 100
                        st.session_state['coin_history'].insert(0, {"날짜": datetime.now().strftime("%Y.%m.%d"), "내용": "오운완 출석 보상", "변동": "+100", "잔액": st.session_state['coins']})
                        st.rerun()
                st.markdown("---")

            elif st.session_state['workout_state'] == "완료":
                st.markdown("### 📸 M13. 오늘 운동 결과 요약")
                planned_items = st.session_state['my_routine']
                planned_count = len(planned_items)
                completed_count = sum(1 for r in planned_items if r.get('완료', False))
                total_sets = len(st.session_state['today_records'])
                total_vol = sum([r.get('중량',0)*r.get('횟수',0) for r in st.session_state['today_records']])
                
                cardio_records = [r['내용'] for r in st.session_state['today_records'] if '내용' in r]
                cardio_str = ", ".join(cardio_records) if cardio_records else "없음"

                ai_fb = get_ai_workout_feedback(current_user_name, planned_count, completed_count, total_sets, total_vol, cardio_str, st.session_state['gemini_api_key'])
                st.success(ai_fb)
                
                st.markdown("### 📅 M27. 다음 운동 약속하기")
                with st.expander("AI 트레이너와 다음 방문일을 약속하고 리마인드를 받아보세요!", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1: next_date = st.date_input("예정일 선택")
                    with c2: next_time = st.time_input("시간 선택")
                    repeat_opt = st.selectbox("반복 일정 설정", ["반복 안함", "매주 같은 요일/시간에 반복"])
                    
                    if st.button("🔔 리마인드 알림 설정", use_container_width=True):
                        st.session_state['next_workout_promise'] = f"{next_date.strftime('%m월 %d일')} {next_time.strftime('%H:%M')}"
                        st.session_state['next_workout_repeat'] = "(매주 반복)" if repeat_opt != "반복 안함" else ""
                        st.toast(f"✅ {st.session_state['next_workout_promise']}에 알림을 보내드릴게요!")
                
                st.markdown("#### 📋 오늘의 루틴 수행 결과")
                for r in planned_items:
                    if r.get('완료', False):
                        st.write(f"✅ **{r.get('기구')}** - 완료")
                    elif r.get('상태') == '건너뜀':
                        st.write(f"⏭️ **{r.get('기구')}** - 건너뜀 (사유: 사용자 선택)")
                    else:
                        st.write(f"⬜ **{r.get('기구')}** - 미완료")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                card_html = f"""
                <div class='owoonwan-card'>
                    <h2>FITPASS PRO</h2>
                    <p style="font-size: 1.2rem; color: #4facfe;">🔥 TODAY'S WORKOUT 🔥</p>
                    <p style="font-size: 1.8rem; font-weight: 900;">@{current_user_name}</p>
                    <hr style="border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">
                    <p style="font-size: 1.1rem;">📅 {datetime.now().strftime('%Y.%m.%d')}</p>
                    <p style="font-size: 1.1rem;">🏃 유산소: {cardio_str}</p>
                    <p style="font-size: 1.1rem;">🏋️ 총 웨이트 볼륨: {total_vol} kg</p>
                    <p style="font-size: 1.1rem;">🔥 달성률: {planned_count}개 중 {completed_count}개 완료</p>
                    <p style="font-size: 1.2rem; color: #ccff00; margin-top: 10px;">🎁 +100 코인 획득!</p>
                </div><br>
                """
                st.markdown(card_html, unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["📊 주간 및 월간 리포트 (M24)", "📈 누적 추이"])
            with tab1:
                st.markdown("#### 🎯 주간 목표 진행률")
                st.progress(1.0, text="주간 방문 목표: 4회 중 4회 완료 (100%)")
                
                st.markdown("#### 📅 M24. 이번 달 요약 리포트")
                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                m_c1.metric("총 운동일", "11일", "+3일")
                m_c2.metric("자주 한 부위", "하체", "전체 55%")
                m_c3.metric("최애 기구", "스쿼트", "총 15세트")
                m_c4.metric("목표 달성률", "85%", "15% 증가")
                
                monthly_ai = get_ai_monthly_feedback(current_user_name, 11, 8, "하체", st.session_state['gemini_api_key'])
                st.info(monthly_ai)

            with tab2:
                st.markdown("#### 📈 M16. 나의 누적 볼륨 추이")
                if '회원명' in history_df.columns:
                    my_history_df = history_df[history_df['회원명'] == current_user_name].copy()
                    if not my_history_df.empty:
                        base = alt.Chart(my_history_df).encode(
                            x=alt.X('날짜:O', axis=alt.Axis(labelAngle=-45, labelColor='white', titleColor='white')),
                            y=alt.Y('총 볼륨(kg):Q', scale=alt.Scale(zero=False), axis=alt.Axis(gridColor='rgba(255,255,255,0.2)', labelColor='white', titleColor='white')),
                            tooltip=['날짜', '주요 기구', '총 볼륨(kg)']
                        )
                        area = base.mark_area(color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='rgba(0, 242, 254, 0.6)', offset=0), alt.GradientStop(color='rgba(0, 242, 254, 0.05)', offset=1)], x1=1, y1=0, y2=1))
                        line = base.mark_line(color='#00f2fe', strokeWidth=3)
                        points = base.mark_circle(color='#ccff00', size=70, stroke='white', strokeWidth=1)
                        chart_history = (area + line + points).properties(height=300).configure(background='transparent').configure_view(strokeWidth=0).configure_axis(domainColor='rgba(255,255,255,0.3)', tickColor='rgba(255,255,255,0.3)')
                        st.altair_chart(chart_history, use_container_width=True, theme=None)
                    else: st.info("기록이 없습니다.")

        elif menu == "🏆 5. 랭킹 및 리워드":
            tab_rank, tab_reward, tab_badge = st.tabs(["🏆 지점 랭킹", "🎁 코인 샵", "🏅 내 배지(M26)"])
            
            with tab_rank:
                st.markdown("### 👑 이번 주 명예의 전당")
                st.caption("※ 주간 방문 횟수 및 총 볼륨을 기준으로 산정됩니다.")
                
                rank_data = pd.DataFrame({
                    "순위": ["1위 🥇", "2위 🥈", "3위 🥉", "4위", "5위"],
                    "회원": ["이광수", "송지효", f"{current_user_name}(나)", "최운식", "김철수"],
                    "주간 방문(일)": [5, 4, 3, 2, 1],
                    "주간 누적 볼륨(kg)": [12500, 9800, 8500, 5400, 3200]
                })
                st.dataframe(rank_data, hide_index=True, use_container_width=True)
                
                st.info(f"💡 **{current_user_name}**님은 현재 **3위**입니다. 조금만 더 힘내세요!")

            with tab_reward:
                st.markdown("### 🎁 포인트 교환소")
                st.markdown(f"<div class='reward-card'>보유 코인: <span class='coin-text'>{st.session_state['coins']} C</span></div>", unsafe_allow_html=True)
                
                def buy_item(item_name, price):
                    if st.session_state['coins'] >= price:
                        st.session_state['coins'] -= price
                        st.session_state['coin_history'].insert(0, {"날짜": datetime.now().strftime("%Y.%m.%d"), "내용": f"{item_name} 교환", "변동": f"-{price}", "잔액": st.session_state['coins']})
                        st.balloons()
                        st.success(f"🎉 '{item_name}' 교환 성공!")
                    else: st.error("❌ 코인이 부족합니다.")

                r_col1, r_col2, r_col3 = st.columns(3)
                with r_col1:
                    st.markdown("<div class='reward-card'>🥤 <b>단백질 쉐이크</b><br>500 C</div>", unsafe_allow_html=True)
                    if st.button("교환하기", key="btn1", use_container_width=True): buy_item("단백질 쉐이크", 500)
                with r_col2:
                    st.markdown("<div class='reward-card'>☕ <b>아메리카노 1잔</b><br>300 C</div>", unsafe_allow_html=True)
                    if st.button("교환하기", key="btn2", use_container_width=True): buy_item("아메리카노 1잔", 300)
                with r_col3:
                    st.markdown("<div class='reward-card'>💪 <b>1:1 PT 1회권</b><br>5,000 C</div>", unsafe_allow_html=True)
                    if st.button("교환하기", key="btn3", use_container_width=True): buy_item("1:1 PT 1회권", 5000)

                st.markdown("#### 📜 획득/사용 내역")
                st.dataframe(pd.DataFrame(st.session_state['coin_history']), hide_index=True, use_container_width=True)

            with tab_badge:
                st.markdown("### 🏅 M26. 운동 게이미피케이션")
                st.write("목표를 달성하고 멋진 칭호와 배지를 모아보세요!")
                badges = [
                    ("🐣", "첫 운동 완료", True), 
                    ("🔥", "주간 목표 달성", True), 
                    ("🏆", "개인 기록 갱신", True), 
                    ("🎯", "월간 목표 달성", False), 
                    ("👑", "4주 연속 달성", False),
                    ("💪", "특정 기구 10회", False)
                ]
                cols = st.columns(len(badges))
                for i, (icon, name, is_acq) in enumerate(badges):
                    with cols[i]:
                        if is_acq: st.markdown(f"<div class='badge-card'><span style='font-size:2rem;'>{icon}</span><br><b style='font-size:0.8rem; color:#ccff00;'>{name}</b></div>", unsafe_allow_html=True)
                        else: st.markdown(f"<div class='badge-card-locked'><span style='font-size:2rem;'>🔒</span><br><b style='font-size:0.8rem; color:gray;'>{name}</b></div>", unsafe_allow_html=True)

        elif menu == "💬 6. 소통 및 설정함":
            tab1, tab2, tab3 = st.tabs(["💬 M21. 1:1 질문", "🛠️ M20. 시설 신고", "⚙️ M22. 환경설정"])
            with tab1:
                q_cat = st.selectbox("문의 유형", ["운동 피드백", "PT 문의", "기타"])
                q_text = st.text_area("질문 내용")
                if st.button("질문 전송"): 
                    new_id = len(st.session_state['qna_db']) + 101 
                    st.session_state['qna_db'].insert(0, {"id": new_id, "시간": "방금전", "회원명": f"{current_user_name}(본인)", "유형": q_cat, "내용": q_text, "상태": "대기중", "답변": ""})
                    st.toast(f"접수 완료! (접수번호: #{new_id})")
                    st.rerun()
                for q in st.session_state['qna_db']:
                    if current_user_name in q.get('회원명', ''): 
                        with st.expander(f"[#{q.get('id', 0)}] {q.get('상태', '대기중')} - {q.get('유형', '')}"): 
                            st.write(f"🙋‍♂️ 질문: {q.get('내용', '')}")
                            if q.get('상태') == '답변완료':
                                st.info(f"👨‍🏫 담당자 답변: {q.get('답변', '')}")
            with tab2:
                f_loc = st.selectbox("불편 발생 위치", ["프리웨이트존", "유산소존", "탈의실"])
                f_text = st.text_area("신고 내용")
                if st.button("신고 전송"):
                    st.session_state['facility_db'].insert(0, {"id": len(st.session_state['facility_db'])+1, "시간": "방금전", "신고자": f"{current_user_name}(본인)", "위치": f_loc, "내용": f_text, "상태": "접수됨", "답변": ""})
                    st.toast("신고 접수 완료!")
                    st.rerun()
            with tab3:
                st.markdown("#### ⚙️ 알림 및 개인화 설정")
                reminders = st.toggle("🔔 필수 서비스 알림 (운동 리마인드 등)", value=st.session_state.get('reminders_on', True))
                if reminders != st.session_state.get('reminders_on', True):
                    st.session_state['reminders_on'] = reminders
                    st.rerun()
                    
                st.toggle("💌 선택 마케팅 알림 (이벤트, 혜택 등)", value=True)
                ai_mode = st.toggle("🤖 AI 개인화 추천 모드 사용", value=st.session_state.get('ai_mode', True))
                if ai_mode != st.session_state.get('ai_mode', True):
                    st.session_state['ai_mode'] = ai_mode
                    st.rerun()

# ==========================================
# 5. 💻 점주 (OWNER) B2B 대시보드
# ==========================================
def owner_app():
    st.sidebar.markdown(f"**🏢 총괄 점주 대시보드**")
    menu = st.sidebar.radio("📋 대시보드 메뉴", [
        "🏠 Epic 0. 오늘의 할 일 홈",
        "🚨 Epic 1. 이탈 위험 관리", 
        "🏆 Epic 2. 우수 회원 관리",
        "🎯 Epic 3. PT 영업 및 성장", 
        "💬 Epic 4. Q&A 및 소통", 
        "🏢 Epic 5. 기구별 혼잡도 분석",
        "🔒 Epic 6. 개인정보 동의",
        "🛠️ Epic 7. 시설 민원 관리",
        "🎉 Epic 8. 이벤트 홍보",
        "🌱 Epic 9. 신규 회원 정착",
        "📅 Epic 10. PT 일정 관리"
    ])

    all_members = df_members['회원명'].tolist() if '회원명' in df_members.columns else []

    if menu == "🏠 Epic 0. 오늘의 할 일 홈":
        st.title("🏠 Epic 0. 오늘의 할 일 홈 화면")
        st.markdown("<div class='corp-card'>점주님이 오늘 당장 처리해야 할 핵심 업무 현황을 요약합니다. (DB 연동)</div>", unsafe_allow_html=True)
        pending_qna = sum(1 for q in st.session_state['qna_db'] if q.get('상태') == '대기중')
        pending_fac = sum(1 for f in st.session_state['facility_db'] if f.get('상태') == '접수됨')
        c1, c2, c3 = st.columns(3)
        c1.metric("🚨 신규 이탈 위험군", f"{len(churn_df)}명", "조치 필요")
        c2.metric("💬 미답변 1:1 질문", f"{pending_qna}건", "대기중")
        c3.metric("🛠 신규 시설 민원", f"{pending_fac}건", "확인 요망")
        c4, c5, c6 = st.columns(3)
        c4.metric("🏆 신규 우수 회원", f"{len(vip_df)}명", "+2명")
        c5.metric("🌱 초기 정착 필요", "8명", "플랜 수립")
        c6.metric("🎯 정체기 돌파 시급", f"{len(sales_df)}명", "PT 제안 타겟")

    elif menu == "🚨 Epic 1. 이탈 위험 관리":
        st.title("🚨 Epic 1. 이탈 위험 신호 관리")
        if not churn_df.empty:
            st.markdown("#### 🔍 이탈 위험 요인 상세 분석")
            factor_data = []
            for member in churn_df['회원명']: factor_data.extend([{"회원명": member, "요인": "방문 빈도 하락", "비중(%)": np.random.randint(40, 70)}, {"회원명": member, "요인": "총 볼륨 감소", "비중(%)": np.random.randint(10, 30)}])
            factor_chart = alt.Chart(pd.DataFrame(factor_data)).mark_bar().encode(x=alt.X('sum(비중(%)):Q', stack='normalize', axis=alt.Axis(format='%')), y='회원명:N', color='요인:N').properties(height=200)
            st.altair_chart(factor_chart, use_container_width=True)
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        default_churn = [m for m in churn_df['회원명'].tolist() if m in all_members] if not churn_df.empty else []
        selected_churn = st.multiselect("발송 대상 선택", options=all_members, default=default_churn)
        if st.button("일괄 자동 컨택 발송", type="primary"): st.toast(f"✅ {len(selected_churn)}명 발송 완료.")

    elif menu == "🏆 Epic 2. 우수 회원 관리":
        st.title("🏆 Epic 2. 우수 회원 자동 선별")
        st.dataframe(vip_df, use_container_width=True, hide_index=True)
        default_vip = [m for m in vip_df['회원명'].tolist() if m in all_members] if not vip_df.empty else []
        selected_vip = st.multiselect("발송 대상 선택", options=all_members, default=default_vip)
        if st.button("VIP 혜택 메시지 발송", type="primary"): st.toast(f"✅ {len(selected_vip)}명 발송 완료.")

    elif menu == "🎯 Epic 3. PT 영업 및 성장":
        st.title("🎯 Epic 3. 정체기 회원 타겟팅 (PT 영업)")
        st.dataframe(sales_df, hide_index=True, use_container_width=True)
        target_opts = sales_df['회원명'].tolist() if not sales_df.empty else all_members
        if target_opts:
            target_member = st.selectbox("분석할 회원 선택:", target_opts)
            if '회원명' in history_df.columns:
                member_hist = history_df[history_df['회원명'] == target_member].copy()
                if not member_hist.empty:
                    line_chart = alt.Chart(member_hist).mark_line(point=True).encode(x=alt.X('날짜:O'), y=alt.Y('중량(kg):Q', scale=alt.Scale(zero=False)), color='주요 기구:N').properties(height=250)
                    st.altair_chart(line_chart, use_container_width=True)
        st.markdown("---")
        st.dataframe(history_df.sort_values(by="날짜", ascending=False), height=200, use_container_width=True)

    elif menu == "💬 Epic 4. Q&A 및 소통":
        st.title("💬 Epic 4. 1:1 질문함 실시간 연동")
        st.markdown("#### 💬 회원 1:1 문의답변 처리")
        for i, q in enumerate(st.session_state['qna_db']):
            if q.get('상태') == '대기중':
                with st.expander(f"[접수번호: #{q.get('id', 0)}] {q.get('유형', '')} - {q.get('회원명', '')}", expanded=True):
                    st.write(f"Q. {q.get('내용', '')}")
                    reply = st.text_area("답장 작성", key=f"ans_{i}")
                    if st.button("답장 발송", key=f"btn_{i}", type="primary"):
                        q['상태'] = '답변완료'; q['답변'] = reply; st.rerun()

    elif menu == "🏢 Epic 5. 기구별 혼잡도 분석":
        st.title("🏢 Epic 5. 기구별 맞춤 혼잡도 분석")
        machine_columns = [col for col in heatmap_df.columns if col != "시간"]
        if 'active_machines' not in st.session_state: st.session_state.active_machines = machine_columns[:2] if machine_columns else []
        st.session_state.active_machines = [m for m in st.session_state.active_machines if m in machine_columns]
        
        if machine_columns:
            cols = st.columns(len(machine_columns))
            for idx, machine in enumerate(machine_columns):
                is_active = machine in st.session_state.active_machines
                btn_style = "primary" if is_active else "secondary"
                with cols[idx]:
                    if st.button(machine, type=btn_style, use_container_width=True, key=f"btn_mac_{idx}"):
                        if is_active: st.session_state.active_machines.remove(machine)
                        else: st.session_state.active_machines.append(machine)
                        st.rerun()
                        
        if '시간' in heatmap_df.columns and st.session_state.active_machines:
            df_melt = heatmap_df[["시간"] + st.session_state.active_machines].melt('시간', var_name='기구', value_name='사용량(%)')
            chart = alt.Chart(df_melt).mark_area(opacity=0.6).encode(x=alt.X('시간:O'), y='사용량(%):Q', color='기구:N').properties(height=350)
            st.altair_chart(chart, use_container_width=True)

    elif menu == "🔒 Epic 6. 개인정보 동의":
        st.title("🔒 Epic 6. 동의 철회 마스킹")
        st.dataframe(pd.DataFrame({"회원명": ["김철수", "박지민(철회)"], "체성분 데이터": ["75.2kg / 35.1kg", "*** (블라인드)"]}), hide_index=True)

    elif menu == "🛠️ Epic 7. 시설 민원 관리":
        st.title("🛠 Epic 7. 실시간 민원 트래킹")
        for i, f in enumerate(st.session_state['facility_db']):
            with st.expander(f"[{f.get('상태', '')}] {f.get('위치', '')} - {f.get('신고자', '')}"):
                col1, col2 = st.columns([1, 3])
                with col1: status = st.selectbox("상태", ["접수됨", "조치중", "조치완료"], index=["접수됨", "조치중", "조치완료"].index(f.get('상태', '접수됨')), key=f"f_stat_{i}")
                with col2: reply = st.text_input("결과", f.get('답변', ''), key=f"f_rep_{i}")
                if st.button("저장", key=f"f_btn_{i}", type="primary"):
                    f['상태'] = status; f['답변'] = reply; st.rerun()

    elif menu == "🎉 Epic 8. 이벤트 홍보":
        st.title("🎉 Epic 8. 기획 이벤트 홍보")
        st.markdown("#### 📊 진행 중인 이벤트 퍼널")
        funnel_chart = alt.Chart(pd.DataFrame({"단계": ["1. 발송", "2. 신청", "3. 참여"], "인원": [150, 45, 30]})).mark_bar(color='#2563EB').encode(x='인원:Q', y=alt.Y('단계:O', sort=["1. 발송", "2. 신청", "3. 참여"])).properties(height=150)
        st.altair_chart(funnel_chart, use_container_width=True)

    elif menu == "🌱 Epic 9. 신규 회원 정착":
        st.title("🌱 Epic 9. 신규 회원 정착 모니터링")
        st.dataframe(pd.DataFrame({"신규 회원명": ["최신규", "이초보"], "가입일": ["D-3", "D-6"]}), hide_index=True)

    elif menu == "📅 Epic 10. PT 일정 관리":
        st.title("📅 Epic 10. PT 일정 최적화")
        st.info("🕒 오늘 15:00 유휴시간 감지됨 (상담 권장)")

# ==========================================
# 6. 🚀 메인 라우팅 
# ==========================================
def main():
    inject_custom_css()
    if not st.session_state['logged_in']:
        st.markdown("<div class='hero-title'>FITPASS PRO</div><div class='hero-subtitle'>스마트 헬스장 데이터 솔루션 MVP</div>", unsafe_allow_html=True)
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown("<div class='login-card'>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("👟 회원 시연 접속", use_container_width=True):
                    st.session_state['logged_in'] = True; st.session_state['role'] = 'MEMBER'; st.rerun()
            with col_b2:
                if st.button("💼 점주 시연 접속", use_container_width=True):
                    st.session_state['logged_in'] = True; st.session_state['role'] = 'OWNER'; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.sidebar.button("🚪 시스템 종료 (권한 다시 선택)"):
            st.session_state['logged_in'] = False; st.session_state['role'] = None; st.rerun()
        if st.session_state['role'] == 'MEMBER': member_app()
        elif st.session_state['role'] == 'OWNER': owner_app()

if __name__ == "__main__":
    main()
