import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import io
import time
from datetime import datetime
import google.generativeai as genai

# ==========================================
# 0. 🤖 Gemini AI 안전 설정
# ==========================================
if 'gemini_api_key' not in st.session_state:
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
def get_ai_workout_feedback(user_name, planned_count, completed_count, total_sets, total_vol, api_key):
    if not api_key or len(api_key) < 10: 
        return f"🗣 (기본 모드) '{user_name}님, 오늘 계획한 {planned_count}개 중 {completed_count}개를 마쳤어요! 지난번 기록보다 잘 하셨네요. 다음엔 상체부터 시작해볼까요?'"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"너는 철저하게 사실 기반으로만 말하는 AI 트레이너야. '{user_name}' 회원이 오늘 계획된 루틴 {planned_count}개 중 {completed_count}개를 완료했어. "
                  f"(오늘 수행한 총 세트는 {total_sets}세트, 볼륨은 {total_vol}kg이야). "
                  f"다음 규칙을 지켜 3문장 이내로 작성해."
                  f"1. 시작은 반드시 '오늘 계획한 {planned_count}개 중 {completed_count}개를 마쳤어요'라는 문장으로 시작."
                  f"2. 철저하게 [관찰값(예: 지난번 기록보다 반복 횟수가 늘었어요)] 기반의 칭찬만 할 것."
                  f"3. 칼로리, 근력 향상 등 의학적 멘트 금지."
                  f"4. '다음에는 상체 운동부터 시작해 볼까요?' 처럼 다음 방문 제안으로 마무리.")
        response = model.generate_content(prompt)
        return f"🗣 AI 트레이너: '{response.text.strip()}'"
    except:
        return f"🗣 (시스템) '{user_name}님, 오늘 계획한 {planned_count}개 중 {completed_count}개를 마쳤어요!'"

# 🔥 [FRD M24 반영] 월간 피드백 전용 AI 함수
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
    "workout": "날짜,회원명,운동 부위,주요 기구,중량(kg),횟수,세트,총 볼륨(kg)\n07.01,박수민,등,랫풀다운,15,12,5,900\n07.02,이광수,등,케이블 로우,45,15,3,2025\n07.03,마동석,하체,레그 익스텐션,140,12,3,5040\n07.03,박수민,가슴,체스트 프레스,40,15,3,1800\n07.04,박수민,가슴,벤치프레스,40,10,4,1600"
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

# ==========================================
# 2. 페이지 및 세션 상태 초기화
# ==========================================
st.set_page_config(page_title="FITPASS PRO", page_icon="⚡", layout="wide")

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'role' not in st.session_state: st.session_state['role'] = None
if 'current_user' not in st.session_state: st.session_state['current_user'] = "박수민"
if 'workout_state' not in st.session_state: st.session_state['workout_state'] = "준비" 
if 'today_records' not in st.session_state: st.session_state['today_records'] = []

# 🔥 새로운 요구사항 세션 변수 
if 'fav_machines' not in st.session_state: st.session_state['fav_machines'] = ["파워 랙 (스쿼트)"] # M25
if 'next_workout_promise' not in st.session_state: st.session_state['next_workout_promise'] = None # M27
if 'coins' not in st.session_state: st.session_state['coins'] = 1200 # M19A
if 'coin_history' not in st.session_state:
    st.session_state['coin_history'] = [{"날짜": "2026.09.28", "내용": "주간 목표 달성", "변동": "+500", "잔액": 1200}]

ROUTINE_DB = {
    "박수민": {
        "theme": "🔥 하체 볼륨업 (근력 증가)",
        "reason": "최근 2주간 상체 대비 하체 운동 빈도가 약 20% 부족했습니다. 오늘은 하체 볼륨을 확실히 채워 신체 밸런스를 맞추는 것을 권장합니다.",
        "routines": [
            {"id": 0, "부위": "워밍업", "기구": "트레드밀 (유산소)", "목표": "속도 6.0 가볍게 걷기", "시간": "10분", "완료": False, "상태": "대기"},
            {"id": 1, "부위": "하체", "기구": "파워 랙 (스쿼트)", "목표": "80kg x 10회 (4세트)", "시간": "15분", "완료": False, "상태": "대기"},
            {"id": 2, "부위": "하체", "기구": "레그 프레스", "목표": "120kg x 12회 (3세트)", "시간": "12분", "완료": False, "상태": "대기"}
        ]
    }
}

MACHINE_INSTRUCTIONS = {
    "파워 랙 (스쿼트)": {
        "img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470",
        "target": "주요 부위: 대퇴사두근, 둔근 (하체 전체)",
        "steps": ["1️⃣ [조절] 바벨 높이를 본인의 어깨선에 맞게 세팅합니다.", "2️⃣ [시작] 바벨을 승모근에 단단히 얹고 가슴을 폅니다.", "3️⃣ [움직임] 엉덩이를 뒤로 빼며 무릎이 발끝 방향을 향하도록 앉았다 일어납니다.", "4️⃣ [종료] 완전히 일어선 후 안전바 위치를 확인하며 바벨을 거치합니다."]
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
    "트레드밀 (유산소)": {
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
# 3. 🎨 커스텀 CSS 
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    @font-face { font-family: 'GmarketSans'; src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); font-weight: 500; }
    @font-face { font-family: 'GmarketSans'; src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff') format('woff'); font-weight: 700; }
    p, h1, h2, h3, h4, h5, h6, label, li, a, button, svg text, canvas { font-family: 'GmarketSans', 'Montserrat', sans-serif !important; letter-spacing: -0.5px; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #1e293b !important; }
    .reward-card { background: rgba(255, 255, 255, 0.05); border: 1px solid #4facfe; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; }
    .coin-text { font-size: 1.5rem; font-weight: bold; color: #ccff00; }
    .badge-card { text-align:center; padding:15px; background:#1e293b; border-radius:12px; border:2px solid #ccff00; margin-bottom:10px; }
    .badge-card-locked { text-align:center; padding:15px; background:#0f172a; border-radius:12px; opacity:0.4; margin-bottom:10px; }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state['role'] == 'MEMBER':
        st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; }
        [data-testid="stMain"] p, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4, [data-testid="stMain"] label, [data-testid="stMain"] li, [data-testid="stMain"] b, [data-testid="stMain"] strong, [data-testid="stMain"] span:not([class*="stIcon"]):not(.material-icons) { color: #ffffff !important; }
        .insta-gradient-text { font-family: 'Montserrat', sans-serif !important; background: linear-gradient(to right, #00f2fe, #4facfe) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-weight: 900 !important; font-size: 2.5rem !important; text-align: center !important; }
        .profile-card { background: rgba(255, 255, 255, 0.1) !important; border-radius: 24px !important; padding: 20px !important; margin-bottom: 20px !important; color: #ffffff !important;}
        .owoonwan-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid #4facfe; border-radius: 15px; padding: 30px; text-align: center; color: white; margin-top: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
        button[kind="primary"] { background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important; color: #111111 !important; border: none !important; border-radius: 12px !important; font-weight: 800 !important; transition: transform 0.2s, box-shadow 0.2s !important; }
        button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4) !important; color: #111111 !important; }
        button[kind="secondary"] { background-color: rgba(255,255,255,0.05) !important; color: #ffffff !important; border: 1px solid #4facfe !important; border-radius: 12px !important; font-weight: 600 !important; transition: transform 0.2s, background-color 0.2s !important; }
        button[kind="secondary"]:hover { transform: translateY(-2px); background-color: rgba(0, 242, 254, 0.2) !important; border-color: #00f2fe !important; color: #ffffff !important; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 4. 📱 회원 (MEMBER) 앱 화면
# ==========================================
def member_app():
    st.sidebar.markdown("**👟 회원 (B2C) 제어판**")
    
    with st.sidebar.expander("⚙️ AI 설정 (관리자용)"):
        input_key = st.text_input("Gemini API Key 입력", value=st.session_state['gemini_api_key'], type="password")
        if st.button("API 연동 확인"):
            if input_key:
                st.session_state['gemini_api_key'] = input_key
                st.success("✅ 키가 저장되었습니다.")

    all_members = df_members['회원명'].tolist() if not df_members.empty else ["박수민"]
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
        
        # 🔥 [FRD M27] 홈 화면 상단에 다음 운동 약속 리마인드 배너 노출
        if st.session_state.get('next_workout_promise'):
            st.info(f"🔔 **AI 리마인드:** {st.session_state['next_workout_promise']}에 운동이 예약되어 있습니다! 오늘도 파이팅!")

        if menu == "📊 1. 인바디 및 목표 설정":
            st.markdown("### 📊 M02. 인바디 업로드 및 분석")
            uploaded_file = st.file_uploader("인바디 결과지 (이미지/PDF) 업로드")
            if uploaded_file is not None:
                with st.spinner("AI가 체성분 데이터를 분석 중입니다..."): time.sleep(1.5)
                st.success(f"✅ 측정일 ({datetime.now().strftime('%Y-%m-%d')}) 데이터 인식 완료!")
                st.info("💡 **AI 분석 요약 (의료진단 배제)**\n\n골격근량 대비 체지방률이 다소 높습니다. 근력 강화를 위해 오늘은 하체 위주의 볼륨 트레이닝을 권장합니다.")
            
            st.selectbox("🎯 최우선 운동 목표", ["근력 증가 (벌크업)", "체중 관리 (다이어트)", "운동 습관 만들기"])
            st.number_input("주당 희망 방문 횟수", min_value=1, max_value=7, value=4)
            if st.button("목표 저장", use_container_width=True): st.toast("목표 저장 완료!")

        elif menu == "🚀 2. 오늘의 처방 (AI 루틴)":
            st.markdown("### 🤖 M03. AI 트레이너 추천 루틴")
            theme = st.session_state.get('routine_theme', '')
            reason = st.session_state.get('routine_reason', '')
            
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
                        if st.button("건너뛰기", key=f"rep_{idx}"):
                            st.session_state['my_routine'][idx]['상태'] = "건너뜀"
                            st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state['workout_state'] == "준비":
                if st.button("💪 운동 시작하기", type="primary", use_container_width=True): 
                    st.session_state['workout_state'] = "진행중"
                    st.toast("🔥 운동 세션이 시작되었습니다! 기구 스캔 탭으로 이동하세요.")
                    st.rerun()

        elif menu == "📡 3. 기구 스캔 (기록/타이머)":
            st.markdown("### 📡 M06. 기구 스캔 및 가이드")
            
            # 🔥 [FRD M25 반영] 즐겨찾기 빠른 접근 메뉴
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
                # 🔥 [FRD M25] 기구 상세화면에 즐겨찾기 등록/해제 토글 제공
                is_fav = selected_machine in st.session_state['fav_machines']
                if st.toggle(f"⭐ '{selected_machine}' 즐겨찾기 설정", value=is_fav):
                    if selected_machine not in st.session_state['fav_machines']:
                        st.session_state['fav_machines'].append(selected_machine)
                else:
                    if selected_machine in st.session_state['fav_machines']:
                        st.session_state['fav_machines'].remove(selected_machine)

                m_info = MACHINE_INSTRUCTIONS.get(selected_machine)
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
                    if st.button("유산소 종료 및 저장", use_container_width=True): 
                        st.session_state['today_records'].append({"기구": selected_machine, "내용": "25분 완료"})
                        st.toast("✅ 유산소 데이터가 저장되었습니다!")
                else:
                    st.markdown("---")
                    st.markdown("#### 📝 운동 기록 입력")
                    c1, c2 = st.columns(2)
                    with c1: weight = st.number_input("중량 (kg)", value=20, step=5)
                    with c2: reps = st.number_input("반복 횟수", value=10, step=1)
                    
                    if st.button("💪 1세트 기록 완료 및 휴식", type="primary", use_container_width=True): 
                        for r in st.session_state['my_routine']:
                            if selected_machine in r.get('기구', ''): r['완료'] = True
                        st.session_state['today_records'].append({"기구": selected_machine, "중량": weight, "횟수": reps})
                        st.toast(f"✅ {selected_machine} 세트 저장됨!")

        elif menu == "📈 4. 리포트 및 오운완(종료)":
            if st.session_state['workout_state'] == "진행중":
                st.markdown("### 🏁 M12. 오늘 운동 종료하기")
                st.warning("🏃 아직 운동 세션이 진행 중입니다. 최종 종료하시겠습니까?")
                if st.button("🚨 최종 종료하고 리포트 보기", type="primary", use_container_width=True):
                    st.session_state['workout_state'] = "완료"
                    # M19A 코인 지급 로직
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
                
                ai_fb = get_ai_workout_feedback(current_user_name, planned_count, completed_count, total_sets, total_vol, st.session_state['gemini_api_key'])
                st.success(ai_fb)
                
                # 🔥 [FRD M27 반영] 다음 운동 약속 및 리마인드 설정
                st.markdown("### 📅 M27. 다음 운동 약속하기")
                with st.expander("AI 트레이너와 다음 방문일을 약속하고 리마인드를 받아보세요!", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1: next_date = st.date_input("예정일 선택")
                    with c2: next_time = st.time_input("시간 선택")
                    if st.button("🔔 리마인드 알림 설정", use_container_width=True):
                        st.session_state['next_workout_promise'] = f"{next_date.strftime('%m월 %d일')} {next_time.strftime('%H:%M')}"
                        st.toast(f"✅ {st.session_state['next_workout_promise']}에 알림을 보내드릴게요!")

                card_html = f"""
                <div class='owoonwan-card'>
                    <h2>FITPASS PRO</h2>
                    <p style="font-size: 1.2rem; color: #4facfe;">🔥 TODAY'S WORKOUT 🔥</p>
                    <p style="font-size: 1.8rem; font-weight: 900;">@{current_user_name}</p>
                    <hr style="border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">
                    <p style="font-size: 1.1rem;">📅 {datetime.now().strftime('%Y.%m.%d')}</p>
                    <p style="font-size: 1.1rem;">🏋️️ 총 볼륨: {total_vol} kg</p>
                    <p style="font-size: 1.2rem; color: #ccff00; margin-top: 10px;">🎁 +100 코인 획득!</p>
                </div><br>
                """
                st.markdown(card_html, unsafe_allow_html=True)

            # 🔥 [FRD M24 반영] 월간/주간 리포트 탭 분리
            tab1, tab2 = st.tabs(["📊 주간 및 월간 리포트", "📈 누적 추이"])
            with tab1:
                st.markdown("#### 🎯 주간 목표 진행률")
                st.progress(1.0, text="주간 방문 목표: 4회 중 4회 완료 (100%)")
                
                st.markdown("#### 📅 M24. 월간 운동 리포트")
                m_c1, m_c2, m_c3 = st.columns(3)
                m_c1.metric("이번 달 운동일", "11일", "+3일 (전월대비)")
                m_c2.metric("자주 한 부위", "하체", "전체 비중 55%")
                m_c3.metric("목표 달성률", "85%", "15% 증가")
                
                # 월간 분석 AI 멘트
                monthly_ai = get_ai_monthly_feedback(current_user_name, 11, 8, "하체", st.session_state['gemini_api_key'])
                st.info(monthly_ai)

            with tab2:
                st.markdown("#### 📈 M16. 나의 누적 볼륨 추이")
                st.caption("차트가 여기에 렌더링됩니다. (Mock 데이터)")

        # 🔥 [FRD M19A, M26 반영] 랭킹, 리워드 및 배지 통합 탭
        elif menu == "🏆 5. 랭킹 및 리워드":
            tab_rank, tab_reward, tab_badge = st.tabs(["🏆 지점 랭킹", "🎁 코인 샵", "🏅 내 배지(M26)"])
            
            with tab_rank:
                st.markdown("### 👑 이번 주 명예의 전당")
                rank_data = pd.DataFrame({"순위": ["1위 🥇", "2위 🥈", "3위 🥉"], "회원": ["이광수", "송지효", f"{current_user_name}(나)"], "주간 방문": [5, 4, 3]})
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

                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.markdown("<div class='reward-card'>🥤 <b>단백질 쉐이크</b><br>500 C</div>", unsafe_allow_html=True)
                    if st.button("교환하기", key="btn1", use_container_width=True): buy_item("단백질 쉐이크", 500)
                with r_col2:
                    st.markdown("<div class='reward-card'>☕ <b>아메리카노 1잔</b><br>300 C</div>", unsafe_allow_html=True)
                    if st.button("교환하기", key="btn2", use_container_width=True): buy_item("아메리카노 1잔", 300)

                st.markdown("#### 📜 획득/사용 내역")
                st.dataframe(pd.DataFrame(st.session_state['coin_history']), hide_index=True, use_container_width=True)

            with tab_badge:
                st.markdown("### 🏅 M26. 운동 게이미피케이션")
                st.write("목표를 달성하고 멋진 칭호와 배지를 모아보세요!")
                badges = [("🐣", "첫 운동 완료", True), ("🔥", "주간 목표 달성", True), ("🏋️", "최대 볼륨 갱신", True), ("🎯", "월간 목표 달성", False), ("👑", "4주 연속 달성", False)]
                cols = st.columns(5)
                for i, (icon, name, is_acq) in enumerate(badges):
                    with cols[i]:
                        if is_acq: st.markdown(f"<div class='badge-card'><span style='font-size:2rem;'>{icon}</span><br><b style='font-size:0.8rem; color:#ccff00;'>{name}</b></div>", unsafe_allow_html=True)
                        else: st.markdown(f"<div class='badge-card-locked'><span style='font-size:2rem;'>🔒</span><br><b style='font-size:0.8rem; color:gray;'>{name}</b></div>", unsafe_allow_html=True)

        elif menu == "💬 6. 소통 및 설정함":
            st.info("환경 설정 및 Q&A 메뉴 (이전과 동일)")

# ==========================================
# 5. 메인 라우팅 (점주 생략)
# ==========================================
def main():
    inject_custom_css()
    if not st.session_state['logged_in']:
        st.markdown("<div class='hero-title'>FITPASS PRO</div><div class='hero-subtitle'>스마트 헬스장 데이터 솔루션 MVP</div>", unsafe_allow_html=True)
        _, col, _ = st.columns([1, 2, 1])
        with col:
            if st.button("👟 회원 시연 접속", use_container_width=True):
                st.session_state['logged_in'] = True; st.session_state['role'] = 'MEMBER'; st.rerun()
    else:
        if st.sidebar.button("🚪 시스템 종료"):
            st.session_state['logged_in'] = False; st.session_state['role'] = None; st.rerun()
        if st.session_state['role'] == 'MEMBER': member_app()

if __name__ == "__main__":
    main()
