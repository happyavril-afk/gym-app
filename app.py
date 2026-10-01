import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import io
import time
from datetime import datetime

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
            if '티겟분류' in df.columns: df.rename(columns={'티겟분류': '타겟분류'}, inplace=True)
            if required_col and required_col not in df.columns: raise ValueError("필수 컬럼 없음")
            return df
    except Exception:
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

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'role' not in st.session_state: st.session_state['role'] = None
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

if 'current_user' not in st.session_state: st.session_state['current_user'] = "박수민"
if 'workout_state' not in st.session_state: st.session_state['workout_state'] = "준비" 
if 'ai_mode' not in st.session_state: st.session_state['ai_mode'] = True 
if 'today_records' not in st.session_state: st.session_state['today_records'] = []

def reset_routine():
    st.session_state['my_routine'] = [
        {"id": 0, "부위": "워밍업", "기구": "트레드밀", "목표": "10분", "완료": False, "상태": "대기"},
        {"id": 1, "부위": "하체", "기구": "스쿼트", "목표": "80kg x 10회", "세트": 4, "완료": False, "상태": "대기"},
        {"id": 2, "부위": "하체", "기구": "레그 프레스", "목표": "120kg x 12회", "세트": 3, "완료": False, "상태": "대기"}
    ]
if 'my_routine' not in st.session_state: reset_routine()

# ==========================================
# 3. 🎨 커스텀 CSS (완벽한 시인성 & Hover 액션 보완)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    @font-face { font-family: 'GmarketSans'; src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff'); font-weight: 500; }
    @font-face { font-family: 'GmarketSans'; src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff') format('woff'); font-weight: 700; }
    
    p, h1, h2, h3, h4, h5, h6, label, li, a, button, svg text, canvas { font-family: 'GmarketSans', 'Montserrat', sans-serif !important; letter-spacing: -0.5px; }
    [data-testid="stDataFrame"] div, [data-testid="stTable"] th, [data-testid="stTable"] td { font-family: 'GmarketSans', sans-serif !important; }
    
    /* 사이드바 글자색 강제 고정 */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #1e293b !important; }
    </style>
    """, unsafe_allow_html=True)

    # ------------------ 로그인(메인) 화면 ------------------
    if not st.session_state['logged_in']:
        st.markdown("""
        <style>
        .stApp { background-image: linear-gradient(rgba(10,10,12,0.6), rgba(10,10,12,0.8)), url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070'); background-size: cover; background-position: center; }
        .hero-title { font-family: 'Montserrat', sans-serif !important; font-size: clamp(4rem, 10vw, 8rem) !important; font-weight: 900; color: #ffffff; text-align: center; margin-top: 15vh; text-shadow: 0 4px 20px rgba(0,0,0,0.8); }
        .hero-subtitle { font-size: clamp(1.5rem, 4vw, 2.5rem) !important; color: #ccff00; text-align: center; font-weight: 700; margin-bottom: 80px; text-shadow: 0 2px 10px rgba(0,0,0,0.8); }
        
        /* 🔥 로그인 버튼: 크기 확대, 반투명 검정 배경, 글자색 고정형 Hover 애니메이션 */
        .stButton>button { 
            border-radius: 20px !important; 
            font-size: clamp(1.5rem, 3vw, 2.5rem) !important; 
            font-weight: 900 !important; 
            padding: 2rem 1rem !important; 
            border: 3px solid #ccff00 !important; 
            color: #ccff00 !important; 
            background: rgba(0, 0, 0, 0.7) !important; 
            backdrop-filter: blur(10px); 
            height: auto !important; 
            transition: transform 0.2s, background-color 0.2s, box-shadow 0.2s !important;
        }
        .stButton>button:hover { 
            background-color: rgba(204, 255, 0, 0.15) !important; 
            transform: translateY(-5px); 
            color: #ccff00 !important; 
            box-shadow: 0 10px 20px rgba(204,255,0,0.3) !important;
        }
        .stButton>button:active { color: #ccff00 !important; }
        </style>
        """, unsafe_allow_html=True)

    # ------------------ 회원(MEMBER) 화면 ------------------
    elif st.session_state['role'] == 'MEMBER':
        st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; }
        
        /* 🔥 바탕색 대비 모든 텍스트 완전 화이트로 강제 고정 */
        [data-testid="stMain"] p, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4, [data-testid="stMain"] label, [data-testid="stMain"] li, [data-testid="stMain"] b, [data-testid="stMain"] strong, [data-testid="stMain"] span:not([class*="stIcon"]):not(.material-icons) { color: #ffffff !important; }
        
        .insta-gradient-text { font-family: 'Montserrat', sans-serif !important; background: linear-gradient(to right, #00f2fe, #4facfe) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-weight: 900 !important; font-size: 2.5rem !important; text-align: center !important; }
        .profile-card { background: rgba(255, 255, 255, 0.1) !important; border-radius: 24px !important; padding: 20px !important; margin-bottom: 20px !important; color: #ffffff !important;}
        .owoonwan-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 2px solid #4facfe; border-radius: 15px; padding: 30px; text-align: center; color: white; margin-top: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
        
        /* 🔥 B2C Primary 버튼 (파란색 그라데이션) */
        button[kind="primary"] { background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important; color: #111111 !important; border: none !important; border-radius: 12px !important; font-weight: 800 !important; transition: transform 0.2s, box-shadow 0.2s !important; }
        button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4) !important; color: #111111 !important; }
        button[kind="primary"]:active { color: #111111 !important; }
        
        /* 🔥 B2C Secondary 버튼 (건너뛰기/변경 등) - 흰색 테두리와 어두운 배경 */
        button[kind="secondary"] { background-color: rgba(255,255,255,0.05) !important; color: #ffffff !important; border: 1px solid #4facfe !important; border-radius: 12px !important; font-weight: 600 !important; transition: transform 0.2s, background-color 0.2s !important; }
        button[kind="secondary"]:hover { transform: translateY(-2px); background-color: rgba(0, 242, 254, 0.2) !important; border-color: #00f2fe !important; color: #ffffff !important; }
        button[kind="secondary"]:active { color: #ffffff !important; }
        button[kind="secondary"]:focus { color: #ffffff !important; }
        </style>
        """, unsafe_allow_html=True)
        
    # ------------------ 점주(OWNER) 화면 ------------------
    elif st.session_state['role'] == 'OWNER':
        st.markdown("""
        <style>
        .stApp { background-color: #F4F7F9 !important; }
        
        /* 🔥 바탕색 대비 모든 텍스트 진한 네이비색으로 강제 고정 */
        [data-testid="stMain"] p, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] h4, [data-testid="stMain"] label, [data-testid="stMain"] li, [data-testid="stMain"] b, [data-testid="stMain"] strong, [data-testid="stMain"] span:not([class*="stIcon"]):not(.material-icons) { color: #1e293b !important; }
        
        .corp-card { background-color: #ffffff !important; border-radius: 12px; padding: 20px; border-left: 5px solid #2563EB; margin-bottom: 20px; color: #1e293b !important;}
        
        /* 🔥 B2B Primary 버튼 (짙은 파란색) */
        button[kind="primary"] { background-color: #2563EB !important; color: #ffffff !important; border-radius: 8px !important; border: none !important; font-weight: 700 !important; transition: transform 0.2s, box-shadow 0.2s !important; }
        button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3) !important; color: #ffffff !important; }
        button[kind="primary"]:active { color: #ffffff !important; }
        
        /* 🔥 B2B Secondary 버튼 (토글 등) - 하얀색 배경 */
        button[kind="secondary"] { background-color: #ffffff !important; color: #1e293b !important; border-radius: 8px !important; border: 1px solid #cbd5e1 !important; font-weight: 600 !important; transition: transform 0.2s, background-color 0.2s !important; }
        button[kind="secondary"]:hover { transform: translateY(-2px); background-color: #eff6ff !important; border-color: #2563EB !important; color: #1e293b !important; }
        button[kind="secondary"]:active { color: #1e293b !important; }
        button[kind="secondary"]:focus { color: #1e293b !important; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 4. 📱 회원 (MEMBER) 앱 화면
# ==========================================
def member_app():
    st.sidebar.markdown("**👟 회원 (B2C) 제어판**")
    all_members = df_members['회원명'].tolist() if not df_members.empty else ["박수민", "이광수", "전소민", "최운식"]
    if "박수민" not in all_members: all_members.insert(0, "박수민")
    
    idx = all_members.index(st.session_state['current_user']) if st.session_state['current_user'] in all_members else 0
    selected_user = st.sidebar.selectbox("👤 데모 회원 전환", all_members, index=idx)
    
    if selected_user != st.session_state['current_user']:
        st.session_state['current_user'] = selected_user
        st.session_state['workout_state'] = "준비"
        st.session_state['today_records'] = []
        reset_routine()
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
        "💬 5. 소통 및 설정함"
    ])

    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<div class='insta-gradient-text'>FITPASS PRO</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-card'><b style='color:#ffffff;'>@{current_user_name}_workout</b>님, 환영합니다!<br><span style='color:#00f2fe !important;'>운동 상태: {st.session_state['workout_state']}</span></div>", unsafe_allow_html=True)
        
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
                st.success(f"🗣 AI 트레이너: '{current_user_name}님, 지난번 스쿼트 기록이 아주 좋았어요! 오늘은 하체 볼륨을 조금 더 늘려볼까요?'")
                st.write("---")
                
                completed_count = sum(1 for r in st.session_state['my_routine'] if r.get('완료', False))
                st.progress(completed_count / len(st.session_state['my_routine']), text=f"루틴 진행률: {completed_count} / {len(st.session_state['my_routine'])} 완료")
                
                for idx, r in enumerate(st.session_state['my_routine']):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        status_mark = "✅" if r.get('완료', False) else ("⏭️" if r.get('상태', '대기') == "건너뜀" else "⬜")
                        st.markdown(f"**{status_mark} [{r.get('부위', '')}] {r.get('기구', '')}** ({r.get('목표', '')})")
                    with col2:
                        if not r.get('완료', False) and r.get('상태', '대기') != "건너뜀":
                            if st.button("건너뛰기/변경", key=f"rep_{idx}"):
                                st.session_state[f"show_exp_{idx}"] = not st.session_state.get(f"show_exp_{idx}", False)
                                st.rerun()

                    if st.session_state.get(f"show_exp_{idx}", False) and not r.get('완료', False):
                        with st.container():
                            reason = st.selectbox("건너뛰는 사유를 알려주세요", ["기구 사용 중(대기 김)", "컨디션 저하/통증", "다른 운동으로 대체"], key=f"rsn_{idx}")
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
            st.markdown("### 📡 M06. NFC 기구 스캔")
            machine_options = ["📱 기구 대기 중...", "🏋️ 파워 랙 (스쿼트)", "💺 벤치프레스 머신", "💪 랫풀다운", "🏃 트레드밀 (유산소)"]
            machine = st.selectbox("가상 NFC 태그 시뮬레이터:", machine_options)
            
            if machine != "📱 기구 대기 중...":
                machine_name = machine.split(" ")[1] 
                
                if "유산소" in machine:
                    st.image("https://images.unsplash.com/photo-1538805060514-97d9cc17730c?q=80&w=1470", use_container_width=True)
                    st.write("🏃 웨어러블 디바이스 연동 시연 중...")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("현재 심박수", "135 bpm")
                    c2.metric("경과 시간", "25:40")
                    c3.metric("소모 칼로리", "210 kcal")
                    if st.button("유산소 종료 및 저장", use_container_width=True): 
                        st.session_state['today_records'].append({"기구": "트레드밀", "내용": "25분 40초 완료"})
                        st.toast("✅ 유산소 데이터가 저장되었습니다!")
                else:
                    st.info(f"💡 **[{machine_name}] 사용법**\n1. 본인 체형에 맞게 패드를 조절합니다.\n2. 반동 없이 동작을 수행합니다.\n※ 통증 발생 시 즉각 중단하세요.")
                    
                    last_w, last_r = 20, 10 
                    if '회원명' in history_df.columns and not history_df[history_df['회원명'] == current_user_name].empty:
                        past = history_df[(history_df['회원명'] == current_user_name) & (history_df['주요 기구'].str.contains(machine_name, na=False))]
                        if not past.empty:
                            last_record = past.sort_values(by="날짜", ascending=False).iloc[0]
                            last_w, last_r = int(last_record.get('중량(kg)', 20)), int(last_record.get('횟수', 10))
                            st.success(f"💡 **지난번 기록:** {last_w}kg x {last_r}회 ({last_record.get('날짜', '')})")
                    
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
                        st.session_state['today_records'].append({"기구": machine_name, "중량": weight, "횟수": reps})
                        st.toast(f"✅ {machine_name} 1세트 추가됨!")
                        
                        bar = st.progress(0, text="⏱️ 60초 휴식 타이머 진행 중...")
                        for p in range(100):
                            time.sleep(0.01) 
                            bar.progress(p + 1, text="⏱️ 60초 휴식 타이머 진행 중...")
                        st.info("🔔 휴식 종료! 다음 세트를 준비하세요.")
                        st.rerun()

        elif menu == "📈 4. 리포트 및 오운완(종료)":
            if st.session_state['workout_state'] == "완료":
                st.markdown("### 📸 M18. 오운완 (오늘 운동 완료)")
                total_sets = len(st.session_state['today_records'])
                total_vol = sum([r.get('중량',0)*r.get('횟수',0) for r in st.session_state['today_records']])
                
                st.info(f"🗣 트레이너: '{current_user_name}님, 수고하셨습니다! 오늘 총 {total_sets}세트를 수행하셨네요.'")
                
                card_html = f"""
                <div class='owoonwan-card'>
                    <h2>FITPASS PRO</h2>
                    <p style="font-size: 1.2rem; color: #4facfe;">🔥 TODAY'S WORKOUT 🔥</p>
                    <p style="font-size: 1.8rem; font-weight: 900;">@{current_user_name}</p>
                    <hr style="border-top: 1px solid rgba(255,255,255,0.2); margin: 20px 0;">
                    <p style="font-size: 1.1rem;">📅 {datetime.now().strftime('%Y.%m.%d')}</p>
                    <p style="font-size: 1.1rem;">🏋️ 총 볼륨: {total_vol} kg</p>
                    <p style="font-size: 1.1rem;">🔥 완료 세트: {total_sets} Sets</p>
                </div>
                <br>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button("📸 인스타그램 스토리에 공유하기", use_container_width=True, type="primary"):
                    st.toast("✅ 이미지가 클립보드에 복사되었습니다!")
                st.markdown("---")

            st.markdown("### 🏆 M14. 주간 목표 진행률")
            st.progress(1.0, text="주간 방문 목표: 4회 중 4회 완료 (100%)")
            st.balloons()
            st.success(f"🎉 축하합니다! 이번 주 출석을 100% 달성했습니다!")

            st.markdown("### 📈 M16. 나의 누적 볼륨 추이")
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

        elif menu == "💬 5. 소통 및 설정함":
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
                            st.write(f"🙋‍♂️️ 질문: {q.get('내용', '')}")
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
                st.toggle("🔔 필수 서비스 알림 (운동 리마인드 등)", value=True)
                st.toggle("💌 선택 마케팅 알림 (이벤트, 혜택 등)", value=True)
                ai_mode = st.toggle("🤖 AI 개인화 추천 모드 사용", value=st.session_state.get('ai_mode', True), help="끄시면 기본 모드로 전환됩니다.")
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
