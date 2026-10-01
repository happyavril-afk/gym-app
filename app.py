import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import io
import time
from datetime import datetime, timedelta

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
    "qna": "id,시간,회원명,유형,내용,상태,답변\n1,오늘 14:20,박수민,🏋️ 운동/자세 피드백,어깨가 결려요.,대기중,\n2,오늘 13:05,김민지,💳 회원권/PT 문의,할인 문의,답변완료,적용됩니다!",
    "facility": "id,시간,신고자,위치,내용,상태,답변\n1,오늘 09:15,이동국,프리웨이트존,조절 핀 불량,접수됨,\n2,어제 21:00,유재석,남자 탈의실,수압이 약해요,조치중,수리 요청함"
}

@st.cache_data(ttl=600)  
def fetch_data(url, fallback_key, required_col=None):
    try:
        if "http" in url:
            df = pd.read_csv(url)
            if not df.empty and len(df.columns) > 0 and '<html' in str(df.columns[0]).lower():
                raise ValueError("시트 접근 권한 제한됨")
            if len(df.columns) == 1 and ',' in df.columns[0]:
                col_name = df.columns[0]
                raw_text = col_name + '\n' + '\n'.join(df[col_name].astype(str).tolist())
                df = pd.read_csv(io.StringIO(raw_text))
            
            df.columns = df.columns.str.strip()
            df = df.dropna(how='all')
            if '티겟분류' in df.columns:
                df.rename(columns={'티겟분류': '타겟분류'}, inplace=True)
                
            if required_col and required_col not in df.columns:
                raise ValueError(f"엉뚱한 데이터 섞임 (필수 컬럼 '{required_col}' 없음)")
                
            return df
    except Exception as e:
        print(f"Fetch Error [{fallback_key}]: {e}")
        pass
    fallback_df = pd.read_csv(io.StringIO(FALLBACK_DATA[fallback_key]))
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

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
if 'qna_db' not in st.session_state:
    qna_records = df_qna_init.to_dict('records')
    for r in qna_records:
        if '상태' not in r: r['상태'] = '대기중'
    st.session_state['qna_db'] = qna_records
if 'facility_db' not in st.session_state:
    fac_records = df_fac_init.to_dict('records')
    for r in fac_records:
        if '상태' not in r: r['상태'] = '접수됨'
    st.session_state['facility_db'] = fac_records

# 🔥 회원용 세션 상태 추가
if 'current_user' not in st.session_state: st.session_state['current_user'] = "박수민"
if 'workout_state' not in st.session_state: st.session_state['workout_state'] = "준비" # 준비, 진행중, 완료
if 'my_routine' not in st.session_state: 
    st.session_state['my_routine'] = [
        {"id": 0, "부위": "워밍업", "기구": "트레드밀 (유산소)", "목표": "10분", "완료": False},
        {"id": 1, "부위": "하체", "기구": "파워 랙 (스쿼트)", "목표": "80kg x 10회 (4세트)", "완료": False},
        {"id": 2, "부위": "하체", "기구": "레그 프레스", "목표": "120kg x 12회 (3세트)", "완료": False}
    ]

# ==========================================
# 3. 🎨 다이내믹 커스텀 CSS
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    @font-face { font-family: 'GmarketSans'; src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); font-weight: 500; }
    @font-face { font-family: 'GmarketSans'; src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff') format('woff'); font-weight: 700; }
    p, h1, h2, h3, h4, h5, h6, label, li, a, button, b, strong, svg text, canvas { font-family: 'GmarketSans', 'Montserrat', sans-serif !important; letter-spacing: -0.5px; }
    [data-testid="stDataFrame"] div, [data-testid="stTable"] th, [data-testid="stTable"] td { font-family: 'GmarketSans', sans-serif !important; }
    span.material-symbols-rounded, span.material-icons, .stIcon, [class*="st-icon"] { font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span:not([class*="stIcon"]):not(.material-icons), [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] strong { color: #1e293b !important; }
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { background-color: #ccff00 !important; border-radius: 50% !important; margin: 10px !important; box-shadow: 0 4px 15px rgba(204, 255, 0, 0.6) !important; opacity: 1 !important; z-index: 999999 !important; }
    [data-testid="collapsedControl"] svg, [data-testid="stSidebarCollapsedControl"] svg { color: #111111 !important; fill: #111111 !important; width: 24px !important; height: 24px !important; }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state['logged_in']:
        st.markdown("""
        <style>
        .stApp { background-image: linear-gradient(rgba(10, 10, 12, 0.55), rgba(10, 10, 12, 0.85)), url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; }
        .hero-title { font-family: 'Montserrat', sans-serif !important; font-size: clamp(3rem, 12vw, 7rem) !important; font-weight: 900; color: #ffffff; text-align: center; margin-top: 15vh; white-space: nowrap; text-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .hero-subtitle { font-size: clamp(1.2rem, 5vw, 2.2rem) !important; color: #ccff00; text-align: center; font-weight: 700; margin-bottom: 80px; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
        .login-card { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; }
        .stButton>button { border-radius: 20px !important; font-size: clamp(1.4rem, 4vw, 2rem) !important; font-weight: 900 !important; padding: 2.5rem 1rem !important; border: 3px solid #ccff00 !important; color: #ccff00 !important; background: rgba(0, 0, 0, 0.6) !important; backdrop-filter: blur(5px); transition: all 0.3s ease !important; height: auto !important; }
        .stButton>button:hover { background: #ccff00 !important; color: #111 !important; transform: scale(1.03); }
        </style>
        """, unsafe_allow_html=True)

    elif st.session_state['role'] == 'MEMBER':
        st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; }
        [data-testid="stMain"] p, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] span:not([class*="stIcon"]):not(.material-icons), [data-testid="stMain"] label, [data-testid="stMain"] li { color: #ffffff !important; }
        .insta-gradient-text { font-family: 'Montserrat', sans-serif !important; background: linear-gradient(to right, #00f2fe, #4facfe) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-weight: 900 !important; font-size: 2.5rem !important; text-align: center !important; }
        .profile-card { background: rgba(255, 255, 255, 0.1) !important; border-radius: 24px !important; padding: 20px !important; margin-bottom: 20px !important; }
        .stButton>button { border-radius: 20px !important; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important; color: #111 !important; border: none !important; font-weight: 800 !important; padding: 1.2rem !important; font-size: 1.2rem !important; height: auto !important;}
        .owoonwan-card { background: linear-gradient(135deg, #2563EB 0%, #4facfe 100%); border-radius: 15px; padding: 30px; text-align: center; color: white; margin-top: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
        </style>
        """, unsafe_allow_html=True)
        
    elif st.session_state['role'] == 'OWNER':
        st.markdown("""
        <style>
        .stApp { background-color: #F4F7F9; }
        .corp-card { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid #2563EB; margin-bottom: 20px; }
        .stButton>button { background-color: #2563EB !important; color: white !important; border-radius: 8px !important; }
        button[kind="primary"] { background-color: #2563EB !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: 700 !important; transition: all 0.2s; }
        button[kind="primary"]:hover { opacity: 0.8; }
        button[kind="secondary"] { background-color: #ffffff !important; color: #1e293b !important; border-radius: 8px !important; border: 1px solid #cbd5e1 !important; font-weight: 500 !important; transition: all 0.2s; }
        button[kind="secondary"]:hover { border-color: #2563EB !important; color: #2563EB !important; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 4. 📱 회원 (MEMBER) 앱 화면 (FRD 반영 전면 재작성)
# ==========================================
def member_app():
    st.sidebar.markdown("**👟 회원 (B2C) 제어판**")
    
    # 🔥 [FRD 반영] M01: 샘플 데모 회원 전환 (세션 관리)
    all_members = df_members['회원명'].tolist() if not df_members.empty else ["박수민", "이광수", "전소민", "최운식"]
    if "박수민" not in all_members: all_members.insert(0, "박수민")
    
    idx = all_members.index(st.session_state['current_user']) if st.session_state['current_user'] in all_members else 0
    selected_user = st.sidebar.selectbox("👤 데모 회원 전환", all_members, index=idx)
    
    if selected_user != st.session_state['current_user']:
        st.session_state['current_user'] = selected_user
        st.session_state['workout_state'] = "준비"
        # 상태 초기화용 루틴 리셋
        st.session_state['my_routine'] = [
            {"id": 0, "부위": "워밍업", "기구": "트레드밀 (유산소)", "목표": "10분", "완료": False},
            {"id": 1, "부위": "하체", "기구": "파워 랙 (스쿼트)", "목표": "80kg x 10회 (4세트)", "완료": False},
            {"id": 2, "부위": "하체", "기구": "레그 프레스", "목표": "120kg x 12회 (3세트)", "완료": False}
        ]
        st.rerun()

    current_user_name = st.session_state['current_user']
    
    # 🔥 [FRD 반영] M12: 오늘 운동 종료 흐름
    if st.session_state['workout_state'] == "진행중":
        if st.sidebar.button("🏁 오늘 운동 마치기", type="primary"):
            st.session_state['workout_state'] = "완료"
            st.rerun()

    menu = st.sidebar.radio("📋 메뉴 선택", [
        "📊 1. 목표 및 인바디 분석",
        "🚀 2. 오늘의 처방 (Today's Fit)", 
        "📡 3. 기구 스캔 및 기록", 
        "📈 4. 리포트 및 오운완 결과", 
        "💬 5. 소통 및 신고함"
    ])

    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<div class='insta-gradient-text'>FITPASS PRO</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-card'><b>@{current_user_name}_workout</b>님, 오늘 하루도 득근하세요! 🔥<br><span style='color:#ccff00;'>상태: {st.session_state['workout_state']}</span></div>", unsafe_allow_html=True)
        
        if menu == "📊 1. 목표 및 인바디 분석":
            st.markdown("### 📊 M02. 인바디 업로드 및 목표 설정")
            # 🔥 [FRD 반영] M02A: 인바디 분석 결과 및 의학적 진단 배제 텍스트
            uploaded_file = st.file_uploader("인바디 결과지 (이미지/PDF) 업로드")
            if uploaded_file is not None:
                with st.spinner("AI가 체성분 데이터를 분석 중입니다..."):
                    time.sleep(1.5)
                st.success(f"✅ 측정일 ({datetime.now().strftime('%Y-%m-%d')}) 데이터 인식 완료!")
                st.info("💡 **AI 트레이너 분석 결과**\n\n현재 골격근량 대비 체지방률이 다소 높은 편입니다. 본 분석은 의료적 진단이 아니며, 근력 강화를 위해 오늘은 하체 위주의 볼륨 트레이닝을 권장합니다.")
            
            st.selectbox("🎯 최우선 운동 목표", ["근력 증가 (벌크업)", "체중 관리 (다이어트)", "운동 습관 만들기", "재활 및 체형 교정"])
            st.number_input("주당 희망 방문 횟수", min_value=1, max_value=7, value=4)
            st.selectbox("오늘 운동 가능 시간", ["30분", "60분", "90분", "120분"])
            
            # 🔥 [FRD 반영] M02: 피하고 싶은 부위 제외 (대체 운동 로직 연동 안내)
            avoid = st.multiselect("피하고 싶은 부위 (부상 등)", ["어깨", "허리", "무릎", "손목"])
            if avoid:
                st.warning(f"⚠️ 선택하신 '{', '.join(avoid)}'에 무리가 가는 기구는 추천 루틴에서 제외되며, 대체 운동이 제안됩니다.")
            
            if st.button("목표 저장 및 AI 분석 시작", use_container_width=True): 
                st.toast("목표가 저장되었습니다. AI 트레이너가 루틴을 갱신합니다!")

        elif menu == "🚀 2. 오늘의 처방 (Today's Fit)":
            st.markdown("### 🤖 M03. AI 트레이너 오늘의 루틴")
            st.success(f"🗣 트레이너: '{current_user_name}님, 지난주 대비 방문이 훌륭해요! 오늘은 분석 결과에 맞춰 하체 위주로 가볼까요?'")
            st.write("---")
            
            # 🔥 [FRD 반영] M03, M05: 체크리스트 관리 및 기구 대체 기능
            completed_count = sum(1 for r in st.session_state['my_routine'] if r['완료'])
            st.progress(completed_count / len(st.session_state['my_routine']), text=f"진행률: {completed_count} / {len(st.session_state['my_routine'])} 완료")
            
            for idx, r in enumerate(st.session_state['my_routine']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    is_done = st.checkbox(f"[{r['부위']}] {r['기구']} - {r['목표']}", value=r['완료'], key=f"chk_{idx}")
                    if is_done != r['완료']:
                        st.session_state['my_routine'][idx]['완료'] = is_done
                        st.rerun()
                with col2:
                    if not r['완료']:
                        if st.button("대체하기", key=f"rep_{idx}"):
                            st.session_state['my_routine'][idx]['기구'] = "스미스 머신 (대체됨)"
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state['workout_state'] == "준비":
                if st.button("💪 운동 시작하기", type="primary", use_container_width=True): 
                    st.session_state['workout_state'] = "진행중"
                    st.toast("🔥 운동 세션이 시작되었습니다! 기구 스캔 탭으로 이동하세요.")
                    st.rerun()
            elif st.session_state['workout_state'] == "진행중":
                st.info("🏃 현재 운동이 진행 중입니다. 기록을 위해 '기구 스캔' 탭을 이용하세요.")

        elif menu == "📡 3. 기구 스캔 (NFC 기록)":
            st.markdown("### 📡 M06. NFC 태그 스캔")
            
            machine_options = [
                "📱 기구 대기 중 (태그해주세요)...", 
                "🏋️ 파워 랙 (스쿼트/하체)", 
                "💺 벤치프레스 머신 (가슴)", 
                "💪 랫풀다운 (등)", 
                "🏃 트레드밀 (유산소)"
            ]
            machine = st.selectbox("가상 NFC 태그 시뮬레이터:", machine_options)
            
            if machine != "📱 기구 대기 중 (태그해주세요)...":
                machine_name = machine.split(" ")[1] # "파워", "벤치프레스", "랫풀다운", "트레드밀" 추출
                
                # 🔥 [FRD 반영] M07: 기구 상세 사용법 안내
                st.info(f"💡 **[{machine_name}] 기본 사용법**\n1. 본인 체형에 맞게 의자/패드를 조절합니다.\n2. 허리를 펴고 반동 없이 동작을 수행합니다.\n※ 통증 발생 시 즉각 중단하고 대체 기구를 이용하세요.")
                
                if "유산소" in machine:
                    st.image("https://images.unsplash.com/photo-1538805060514-97d9cc17730c?q=80&w=1470&auto=format&fit=crop", use_container_width=True)
                    # 🔥 [FRD 반영] M10, M10A: 웨어러블 유산소 연동 시나리오 데모
                    st.write("🏃 웨어러블 디바이스 연동 중... (데모)")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("현재 심박수", "135 bpm", "+12 bpm")
                    c2.metric("경과 시간", "25:40")
                    c3.metric("소모 칼로리", "210 kcal")
                    if st.button("유산소 기록 저장", use_container_width=True): 
                        st.toast("✅ 유산소 운동 데이터가 저장되었습니다!")
                else:
                    if "파워" in machine: st.image("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop", use_container_width=True)
                    elif "벤치프레스" in machine: st.image("https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=1470&auto=format&fit=crop", use_container_width=True)
                    elif "랫풀다운" in machine: st.image("https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=1470&auto=format&fit=crop", use_container_width=True)
                    
                    # 🔥 [FRD 반영] M08: 시트에서 해당 회원의 직전 기록 동적으로 불러오기
                    last_w, last_r = 20, 10 # 기본값
                    is_new = True
                    if '회원명' in history_df.columns and '주요 기구' in history_df.columns:
                        # 기구명 부분 매칭 (예: "랫풀다운" in "랫풀다운")
                        past_records = history_df[(history_df['회원명'] == current_user_name) & (history_df['주요 기구'].str.contains(machine_name, na=False))]
                        if not past_records.empty:
                            last_record = past_records.sort_values(by="날짜", ascending=False).iloc[0]
                            last_w = int(last_record.get('중량(kg)', 20))
                            last_r = int(last_record.get('횟수', 10))
                            is_new = False
                            st.success(f"💡 **지난번 기록 적용됨:** {last_w}kg x {last_r}회 (마지막 저장일: {last_record.get('날짜', '')})")
                    
                    if is_new:
                        st.info("💡 이 기구의 첫 기록입니다. 가벼운 무게부터 시작해 보세요!")

                    c1, c2 = st.columns(2)
                    with c1: weight = st.number_input("중량 (kg)", value=last_w, step=5)
                    with c2: reps = st.number_input("반복 횟수", value=last_r, step=1)
                    
                    # 🔥 [FRD 반영] M09, M11: 카운트 시작 및 60초 휴식 타이머 UI
                    if st.button("🔊 카운트 시작 (음성 시연)", use_container_width=True): 
                        st.toast("하나! 둘! 셋! (AI 카운트 음원 재생 중...)")
                        
                    if st.button("💪 현재 세트 기록 저장 및 휴식", type="primary", use_container_width=True): 
                        st.success(f"✅ {machine_name} 1세트 저장 완료!")
                        # 시연용 타이머 프로그레스 바 로직 (빠르게 진행)
                        bar = st.progress(0, text="⏱️ 60초 휴식 타이머 진행 중...")
                        for p in range(100):
                            time.sleep(0.01) 
                            bar.progress(p + 1, text="⏱️ 60초 휴식 타이머 진행 중...")
                        st.info("🔔 휴식 종료! 다음 세트를 준비하세요.")

        elif menu == "📈 4. 리포트 및 오운완 결과":
            st.markdown("### 🏆 M14. 주간 목표 진행률")
            st.progress(1.0, text="주간 방문 목표: 4회 중 4회 완료 (100%)")
            
            # 🔥 [FRD 반영] M19: 목표 달성 축하 메시지 및 애니메이션
            st.balloons()
            st.success(f"🎉 축하합니다! 이번 주 출석 목표를 모두 달성하여 **'이번주 하체왕'** 배지를 획득하셨습니다!")

            # 🔥 [FRD 반영] M13, M18: 운동 종료 시 결과 요약 및 오운완 카드 생성
            if st.session_state['workout_state'] == "완료":
                st.markdown("---")
                st.markdown("### 📸 M18. 오늘의 운동 완료 (오운완)")
                st.info(f"🗣️ AI 트레이너: '{current_user_name}님, 오늘 계획한 3개 중 2개를 마쳤어요. 내일은 상체 운동부터 시작해 볼까요?'")
                
                # HTML/CSS 기반 직관적인 오운완 카드 디자인 (민감정보 제외)
                card_html = f"""
                <div class='owoonwan-card'>
                    <h2>FITPASS PRO</h2>
                    <p style="font-size: 1.2rem; margin-bottom: 5px;">🔥 TODAY'S WORKOUT 🔥</p>
                    <p style="font-size: 1.5rem; font-weight: bold;">@{current_user_name}</p>
                    <hr style="border-top: 1px solid rgba(255,255,255,0.3); margin: 15px 0;">
                    <p>📅 {datetime.now().strftime('%Y.%m.%d')}</p>
                    <p>⏱️ 운동 시간: 1시간 15분</p>
                    <p>🏋️ 완료 기구: 트레드밀, 파워 랙</p>
                </div>
                <br>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button("인스타그램 스토리에 공유하기", use_container_width=True, type="primary"):
                    st.toast("✅ 오운완 이미지가 클립보드에 복사되었습니다!")

            st.markdown("---")
            st.markdown("### 📈 M16. 나의 누적 볼륨 성장 추이")
            
            if '회원명' in history_df.columns and '날짜' in history_df.columns:
                # 🔥 로그인한 본인(current_user_name) 기록만 필터링 보안
                my_history_df = history_df[history_df['회원명'] == current_user_name].copy()
                
                if not my_history_df.empty:
                    base = alt.Chart(my_history_df).encode(
                        x=alt.X('날짜:O', sort=None, axis=alt.Axis(labelAngle=-45, title='날짜', grid=False, labelColor='white', titleColor='white')),
                        y=alt.Y('총 볼륨(kg):Q', scale=alt.Scale(zero=False), axis=alt.Axis(title='총 볼륨(kg)', grid=True, gridColor='rgba(255,255,255,0.2)', labelColor='white', titleColor='white')),
                        tooltip=['날짜', '운동 부위', '주요 기구', '총 볼륨(kg)']
                    )
                    area = base.mark_area(
                        color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='rgba(0, 242, 254, 0.6)', offset=0), alt.GradientStop(color='rgba(0, 242, 254, 0.05)', offset=1)], x1=1, x2=1, y1=0, y2=1)
                    )
                    line = base.mark_line(color='#00f2fe', strokeWidth=3, interpolate='monotone')
                    points = base.mark_circle(color='#ccff00', size=70, opacity=1, stroke='white', strokeWidth=1)
                    
                    chart_history = (area + line + points).properties(height=350).configure(background='transparent').configure_view(strokeWidth=0).configure_axis(domainColor='rgba(255,255,255,0.3)', tickColor='rgba(255,255,255,0.3)')
                    st.altair_chart(chart_history, use_container_width=True, theme=None)
                    
                    with st.expander("📝 전체 기록 상세 보기"): 
                        st.dataframe(my_history_df.drop(columns=['회원명']).sort_values(by="날짜", ascending=False), hide_index=True, use_container_width=True)
                else:
                    st.info("아직 운동 기록이 없습니다. 오늘 첫 운동을 시작해 보세요!")
            else:
                st.warning("데이터 통신 지연: 일시적으로 기록 탭을 불러올 수 없습니다.")

        elif menu == "💬 5. 소통 및 신고함":
            tab1, tab2, tab3 = st.tabs(["💬 M21. 1:1 질문", "🛠️ M20. 시설 신고", "⚙️ M22. 설정"])
            with tab1:
                q_cat = st.selectbox("유형", ["운동 피드백", "PT 문의", "기타"])
                q_text = st.text_area("질문 내용")
                if st.button("질문 전송"): 
                    st.session_state['qna_db'].insert(0, {"id": len(st.session_state['qna_db'])+1, "시간": "방금전", "회원명": f"{current_user_name}(본인)", "유형": q_cat, "내용": q_text, "상태": "대기중", "답변": ""})
                    st.toast("접수 완료!")
                    st.rerun()
                for i, q in enumerate(st.session_state['qna_db']):
                    if current_user_name in q.get('회원명', ''): 
                        with st.expander(f"[{q.get('상태', '대기중')}] {q.get('유형', '')}"): st.write(f"Q: {q.get('내용', '')}\nA: {q.get('답변', '')}")
            with tab2:
                f_loc = st.selectbox("위치", ["프리웨이트존", "유산소존", "탈의실"])
                f_text = st.text_area("신고 내용")
                if st.button("신고 전송"):
                    st.session_state['facility_db'].insert(0, {"id": len(st.session_state['facility_db'])+1, "시간": "방금전", "신고자": f"{current_user_name}(본인)", "위치": f_loc, "내용": f_text, "상태": "접수됨", "답변": ""})
                    st.toast("신고 접수 완료!")
                    st.rerun()
                for i, f in enumerate(st.session_state['facility_db']):
                    if current_user_name in f.get('신고자', ''): 
                        with st.expander(f"[{f.get('상태', '접수됨')}] {f.get('위치', '')}"): st.write(f"{f.get('내용', '')}\n(조치: {f.get('답변', '')})")
            with tab3:
                st.markdown("#### 알림 및 관리 메시지 설정")
                st.toggle("🔔 필수 서비스 알림 (운동 리마인드 등)", value=True)
                st.toggle("💌 선택 마케팅 혜택 알림 (이벤트, 오프피크 쿠폰 등)", value=True)

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
        c3.metric("🛠️ 신규 시설 민원", f"{pending_fac}건", "확인 요망")
        c4, c5, c6 = st.columns(3)
        c4.metric("🏆 신규 우수 회원", f"{len(vip_df)}명", "+2명")
        c5.metric("🌱 초기 정착 필요", "8명", "플랜 수립")
        c6.metric("🎯 정체기 돌파 시급", f"{len(sales_df)}명", "PT 제안 타겟")

    elif menu == "🚨 Epic 1. 이탈 위험 관리":
        st.title("🚨 Epic 1. 이탈 위험 신호 관리")
        if not churn_df.empty:
            st.markdown("#### 🔍 이탈 위험 요인 상세 분석")
            factor_data = []
            for member in churn_df['회원명']:
                factor_data.extend([{"회원명": member, "요인": "방문 빈도 하락", "비중(%)": np.random.randint(40, 70)}, {"회원명": member, "요인": "총 볼륨 감소", "비중(%)": np.random.randint(10, 30)}, {"회원명": member, "요인": "평균 체류시간 감소", "비중(%)": np.random.randint(10, 30)}])
            df_factor = pd.DataFrame(factor_data)
            factor_chart = alt.Chart(df_factor).mark_bar().encode(
                x=alt.X('sum(비중(%)):Q', stack='normalize', axis=alt.Axis(format='%', title='요인별 비중')),
                y=alt.Y('회원명:N', title='회원명'),
                color=alt.Color('요인:N', scale=alt.Scale(scheme='set2')),
                tooltip=['회원명', '요인', '비중(%)']
            ).properties(height=250)
            st.altair_chart(factor_chart, use_container_width=True)
            
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### 📨 맞춤형 복귀 유도 컨택")
        default_churn = [m for m in churn_df['회원명'].tolist() if m in all_members] if not churn_df.empty else []
        selected_churn = st.multiselect("발송 대상 선택 및 편집", options=all_members, default=default_churn)
        msg_template = st.text_area("메시지 내용 수정", "회원님, 최근 방문이 뜸하시네요! 이번 주 오시면 특별한 혜택을 드립니다.")
        if st.button("일괄 자동 컨택 발송", type="primary"): 
            st.toast(f"✅ {len(selected_churn)}명의 회원에게 복귀 유도 메시지가 발송되었습니다.")

    elif menu == "🏆 Epic 2. 우수 회원 관리":
        st.title("🏆 Epic 2. 우수 회원 자동 선별")
        st.dataframe(vip_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### 🎁 VIP 전용 혜택 발송")
        default_vip = [m for m in vip_df['회원명'].tolist() if m in all_members] if not vip_df.empty else []
        selected_vip = st.multiselect("발송 대상 선택 및 편집", options=all_members, default=default_vip)
        msg_vip = st.text_area("메시지 내용 수정", "회원님, 꾸준한 출석과 성장을 축하드립니다! VIP 전용 재등록 쿠폰을 발급해 드렸습니다.")
        if st.button("선택 회원 재등록 쿠폰/감사 메시지 발송", type="primary"): 
            st.toast(f"✅ {len(selected_vip)}명의 VIP 회원에게 혜택이 발송되었습니다.")

    elif menu == "🎯 Epic 3. PT 영업 및 성장":
        st.title("🎯 Epic 3. 정체기 회원 타겟팅 (PT 영업)")
        st.dataframe(sales_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 📉 개별 회원 정체기 정밀 시계열 분석")
        target_opts = sales_df['회원명'].tolist() if not sales_df.empty else all_members
        if target_opts:
            target_member = st.selectbox("분석할 회원 선택:", target_opts)
            if '회원명' in history_df.columns:
                member_hist = history_df[history_df['회원명'] == target_member].copy()
                if not member_hist.empty:
                    line_chart = alt.Chart(member_hist).mark_line(point=True).encode(
                        x=alt.X('날짜:O', axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('중량(kg):Q', scale=alt.Scale(zero=False)),
                        color='주요 기구:N',
                        tooltip=['날짜', '운동 부위', '주요 기구', '중량(kg)']
                    ).properties(height=300)
                    st.altair_chart(line_chart, use_container_width=True)
                else:
                    st.info(f"{target_member} 회원의 상세 운동 기록이 존재하지 않습니다.")

        st.markdown("---")
        st.markdown("#### 🎟️ 원포인트 PT 영업 쿠폰 발송")
        default_sales = [m for m in sales_df['회원명'].tolist() if m in all_members] if not sales_df.empty else []
        selected_sales = st.multiselect("발송 대상 선택 및 편집", options=all_members, default=default_sales)
        msg_sales = st.text_area("메시지 내용 수정", "회원님, 최근 운동 중량이 정체되셨나요? 정확한 자세 교정을 위한 원포인트 PT 무료 쿠폰을 보내드립니다!")
        if st.button("맞춤형 원포인트 PT 쿠폰 일괄 발송", type="primary"): 
            st.toast(f"✅ {len(selected_sales)}명의 회원에게 영업 쿠폰이 발송되었습니다.")
            
        st.markdown("<br><h4>📊 전체 회원 운동 로그 열람 (B2B 관리자용)</h4>", unsafe_allow_html=True)
        st.dataframe(history_df.sort_values(by="날짜", ascending=False), height=200, use_container_width=True)

    elif menu == "💬 Epic 4. Q&A 및 소통":
        st.title("💬 Epic 4. 1:1 질문함 실시간 연동")
        
        st.markdown("#### 📈 주간 AI 자동 발송 및 전환 트렌드")
        dates = pd.date_range(end=pd.Timestamp.today(), periods=7).strftime('%m.%d').tolist()
        ai_data = pd.DataFrame({"날짜": dates * 3, "유형": ["목표 달성 축하(자동)"]*7 + ["정체기 동기부여(자동)"]*7 + ["오프피크 쿠폰(자동)"]*7, "발송건수": np.random.randint(2, 15, size=21)})
        ai_chart = alt.Chart(ai_data).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X('날짜:O', axis=alt.Axis(labelAngle=0)), y=alt.Y('발송건수:Q'), color=alt.Color('유형:N', scale=alt.Scale(scheme='category10')), tooltip=['날짜', '유형', '발송건수']
        ).properties(height=250)
        st.altair_chart(ai_chart, use_container_width=True)
        st.info("💡 금주 AI 추천 운동 평균 완료율: **78.4%** (전주 대비 3.1% 상승)")
        st.markdown("---")

        st.markdown("#### 💬 회원 1:1 문의답변 처리")
        for i, q in enumerate(st.session_state['qna_db']):
            if q.get('상태') == '대기중':
                with st.expander(f"[대기중] {q.get('유형', '')} - {q.get('회원명', '')}", expanded=True):
                    st.write(f"Q. {q.get('내용', '')}")
                    reply = st.text_area("답장 작성", key=f"ans_{i}_{q.get('id', 0)}")
                    if st.button("답장 발송", key=f"btn_{i}_{q.get('id', 0)}", type="primary"):
                        q['상태'] = '답변완료'; q['답변'] = reply; st.rerun()

    elif menu == "🏢 Epic 5. 기구별 혼잡도 분석":
        st.title("🏢 Epic 5. 기구별 맞춤 혼잡도 분석")
        
        if '시간' not in heatmap_df.columns:
            st.error("🚨 앗! 구글 시트 3번째 탭(혼잡도)에 잘못된 데이터가 붙여넣기 된 것 같습니다. 탭 내용을 확인해주세요.")
            
        st.write("구글 스프레드시트의 시간대별 점유율 데이터를 기반으로 시각화합니다.")
        machine_columns = [col for col in heatmap_df.columns if col != "시간"]
        
        if 'active_machines' not in st.session_state:
            preferred = ["파워 랙 (웨이트)", "트레드밀 (유산소)"]
            st.session_state.active_machines = [m for m in preferred if m in machine_columns]
            if not st.session_state.active_machines and machine_columns:
                st.session_state.active_machines = machine_columns[:2]
        
        st.session_state.active_machines = [m for m in st.session_state.active_machines if m in machine_columns]
        st.markdown("**조회할 기구 선택 (다중 선택 가능):**")
        
        if machine_columns:
            cols = st.columns(len(machine_columns))
            for idx, machine in enumerate(machine_columns):
                is_active = machine in st.session_state.active_machines
                btn_style = "primary" if is_active else "secondary"
                with cols[idx]:
                    if st.button(machine, type=btn_style, use_container_width=True, key=f"btn_mac_{idx}"):
                        if is_active:
                            st.session_state.active_machines.remove(machine)
                        else:
                            st.session_state.active_machines.append(machine)
                        st.rerun()
                        
        selected_machines = st.session_state.active_machines
        
        if not selected_machines:
            st.warning("선택된 기구가 없습니다. 위 버튼을 눌러 기구를 선택해주세요.")
        elif '시간' in heatmap_df.columns:
            cols_to_keep = ["시간"] + selected_machines
            filtered_df = heatmap_df[cols_to_keep]
            df_melt = filtered_df.melt('시간', var_name='기구', value_name='사용량(%)')
            chart = alt.Chart(df_melt).mark_area(opacity=0.6).encode(
                x=alt.X('시간:O', axis=alt.Axis(labelAngle=-45, title='시간대')), 
                y=alt.Y('사용량(%):Q', stack=None, axis=alt.Axis(title='누적 점유율(%)')), 
                color=alt.Color('기구:N', legend=alt.Legend(title="선택된 기구")),
                tooltip=['시간', '기구', '사용량(%)']
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
            
        st.markdown("---")
        st.markdown("#### 📉 오프피크(낮 시간대) 마케팅 발송")
        default_offpeak = ["전소민", "김철수"] if all(x in all_members for x in ["전소민", "김철수"]) else all_members[:2]
        selected_offpeak = st.multiselect("낮 시간대 방문 이력 회원 (대상 편집)", options=all_members, default=default_offpeak)
        msg_offpeak = st.text_area("메시지 내용 수정", "회원님, 붐비지 않는 낮 시간(13시~16시)에 방문하시면 프로틴 음료 1잔 무료 쿠폰을 드립니다!")
        if st.button("특정 시간대 방문 회원 '오프피크 마케팅' 일괄 발송", type="primary"): 
            st.toast(f"✅ {len(selected_offpeak)}명의 회원에게 오프피크 마케팅 쿠폰이 발송되었습니다.")

    elif menu == "🔒 Epic 6. 개인정보 동의":
        st.title("🔒 Epic 6. 동의 철회 마스킹")
        privacy_df = pd.DataFrame({"회원명": ["김철수", "박지민(철회)"], "체중/체성분 데이터": ["75.2kg / 35.1kg", "*** / *** (블라인드)"]})
        st.dataframe(privacy_df, hide_index=True, use_container_width=True)

    elif menu == "🛠️ Epic 7. 시설 민원 관리":
        st.title("🛠 Epic 7. 실시간 민원 트래킹")
        for i, f in enumerate(st.session_state['facility_db']):
            with st.expander(f"[{f.get('상태', '')}] {f.get('위치', '')} - {f.get('신고자', '')}"):
                st.write(f"민원: {f.get('내용', '')}")
                col1, col2 = st.columns([1, 3])
                status_list = ["접수됨", "조치중", "조치완료"]
                idx = status_list.index(f['상태']) if f.get('상태') in status_list else 0
                with col1: status = st.selectbox("상태", status_list, index=idx, key=f"f_stat_{i}_{f.get('id', 0)}")
                with col2: reply = st.text_input("결과", f.get('답변', ''), key=f"f_rep_{i}_{f.get('id', 0)}")
                if st.button("저장", key=f"f_btn_{i}_{f.get('id', 0)}", type="primary"):
                    f['상태'] = status; f['답변'] = reply; st.rerun()

    elif menu == "🎉 Epic 8. 이벤트 홍보":
        st.title("🎉 Epic 8. 기획 이벤트 타겟 홍보 및 관리")
        st.markdown("#### 📊 현재 진행 중인 이벤트 퍼널(Funnel) 현황")
        funnel_data = pd.DataFrame({"단계": ["1. 안내 발송", "2. 신청 완료", "3. 참여 중", "4. 목표 달성"], "인원(명)": [150, 45, 30, 8]})
        funnel_chart = alt.Chart(funnel_data).mark_bar(color='#2563EB').encode(
            x=alt.X('인원(명):Q'), y=alt.Y('단계:O', sort=["1. 안내 발송", "2. 신청 완료", "3. 참여 중", "4. 목표 달성"]), tooltip=['단계', '인원(명)']
        ).properties(height=200)
        st.altair_chart(funnel_chart, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 📣 신규 이벤트 PUSH 발송 설정")
        event_name = st.text_input("이벤트 명", "여름 맞이 바디프로필 챌린지")
        event_filter = st.selectbox("타겟 필터링 (자동 분류)", ["전체 회원", "최근 1개월 가입자", "주 3회 이상 출석 VIP"])
        default_event = all_members if event_filter == "전체 회원" else ([m for m in vip_df['회원명'].tolist() if m in all_members] if not vip_df.empty else [])
        selected_event = st.multiselect("최종 발송 대상 확인 및 편집", options=all_members, default=default_event)
        msg_event = st.text_area("안내 메시지 수정", f"[{event_name}] 회원님을 위한 특별한 이벤트가 시작되었습니다! 지금 헬스장 앱에서 내용을 확인하고 바로 신청해 보세요.")
        if st.button("이벤트 안내 PUSH 일괄 발송", type="primary"): 
            st.toast(f"✅ {len(selected_event)}명의 회원에게 이벤트 배포가 완료되었습니다.")

    elif menu == "🌱 Epic 9. 신규 회원 정착":
        st.title("🌱 Epic 9. 신규 회원 초기 정착 모니터링")
        onboard_df = pd.DataFrame({"신규 회원명": ["최신규", "이초보"], "가입일": ["D-3", "D-6"], "인바디 등록": ["완료", "미등록"], "첫 방문": ["미방문", "미방문"]})
        st.dataframe(onboard_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 🤝 초기 정착 지원 안내 발송")
        default_onboard = ["최신규", "이초보"] 
        full_onboard_opts = list(set(all_members + default_onboard)) 
        selected_onboard = st.multiselect("안내가 필요한 신규 회원", options=full_onboard_opts, default=default_onboard)
        msg_onboard = st.text_area("안내 메시지 수정", "회원님, 가입을 진심으로 환영합니다! 기구 사용법이나 운동 플랜이 궁금하시다면 언제든 앱을 통해 1:1 질문을 남겨주세요.")
        if st.button("앱 이용 안내 및 운동 플랜 독려 알림 발송", type="primary"): 
            st.toast(f"✅ {len(selected_onboard)}명의 신규 회원에게 정착 유도 알림이 발송되었습니다.")

    elif menu == "📅 Epic 10. PT 일정 관리":
        st.title("📅 Epic 10. 유휴시간(PT Schedule) 최적화")
        
        st.markdown("#### 🗓️ 주간 PT 일정 및 타임테이블")
        hours = [f"{h}:00" for h in range(9, 22)]
        days = ["월", "화", "수", "목", "금", "토"]
        timetable = pd.DataFrame(index=hours, columns=days)
        timetable.fillna("", inplace=True)
        timetable.loc["10:00", "월"] = "PT (김철수)"
        timetable.loc["11:00", "화"] = "PT (송지효)"
        timetable.loc["15:00", "수"] = "유휴 시간 (상담 추천)"
        timetable.loc["18:00", "목"] = "PT (이광수)"
        timetable.loc["19:00", "금"] = "PT (마동석)"
        timetable.loc["14:00", "토"] = "유휴 시간 (순회 지도)"
        
        def color_schedule(val):
            if 'PT' in val: return 'background-color: #dbeafe; color: #1e40af; font-weight: bold;'
            elif '유휴' in val: return 'background-color: #fef08a; color: #854d0e; font-weight: bold;'
            return ''
            
        st.dataframe(timetable.style.map(color_schedule), use_container_width=True)

        st.markdown("---")
        st.markdown("#### ⚡ 유휴 시간대 추천 액션")
        st.info("🕒 수요일 15:00, 토요일 14:00 유휴시간이 감지되었습니다.")
        st.checkbox("추천 1: 정체기 회원(최운식) 원포인트 순회 지도")
        st.checkbox("추천 2: 신규 회원(이초보) 등록 상담 콜")
        st.checkbox("추천 3: 센터 기구(케이블 머신) 점검 및 정비")
        if st.button("선택한 일정 확정 및 캘린더 등록", type="primary"): 
            st.toast("✅ 일정표에 성공적으로 등록되었습니다.")

# ==========================================
# 6. 🚀 메인 라우팅 (컨트롤 타워)
# ==========================================
def main():
    inject_custom_css()
    
    if not st.session_state['logged_in']:
        st.markdown("<div class='hero-title'>FITPASS PRO</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-subtitle'>스마트 헬스장 데이터 솔루션 B2B2C MVP</div>", unsafe_allow_html=True)
        
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
