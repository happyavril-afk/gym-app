import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import io
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

# [안전장치] 통신 실패 시 앱 구동을 보장하는 예비(Fallback) 데이터 
FALLBACK_DATA = {
    "member": "회원명,가입일,잔여일,주평균방문,방문추세,볼륨증감률(%),정체종목,정체기간(주),이탈확률(%),타겟분류\n김철수,2025.11.15,45,1.2,감소 📉,-15,없음,0,88,이탈위험\n박지민,2026.01.10,120,1.5,감소 📉,-10,없음,0,75,이탈위험\n이광수,2024.05.10,150,4.5,증가 📈,12,없음,0,5,VIP\n송지효,2023.11.22,210,5.1,증가 📈,22,없음,0,2,VIP\n최운식,2025.05.15,180,3.0,유지 ➖,2,스쿼트,4,25,정체기\n전소민,2026.02.28,60,2.5,유지 ➖,0,숄더 프레스,3,40,정체기",
    "workout": "날짜,운동 부위,주요 기구,중량(kg),횟수,세트,총 볼륨(kg)\n08.20,하체,레그 프레스,100,10,3,3000\n08.22,가슴,벤치프레스,60,12,4,2880\n08.25,등,랫풀다운,45,15,3,2025\n08.28,하체,스쿼트,80,10,4,3200\n09.01,어깨,숄더 프레스,30,12,3,1080\n09.05,가슴,체스트 프레스,50,15,3,2250",
    "heatmap": "시간,파워 랙 (웨이트),트레드밀 (유산소),스미스 머신,스트레칭존,케이블 머신\n06:00,10,25,5,15,10\n09:00,25,45,15,20,25\n12:00,30,35,25,25,40\n15:00,50,60,40,30,55\n18:00,95,100,85,60,90",
    "qna": "id,시간,회원명,유형,내용,상태,답변\n1,오늘 14:20,박수민,🏋️ 운동/자세 피드백,어깨가 결려요.,대기중,\n2,오늘 13:05,김민지,💳 회원권/PT 문의,할인 문의,답변완료,적용됩니다!",
    "facility": "id,시간,신고자,위치,내용,상태,답변\n1,오늘 09:15,이동국,프리웨이트존,조절 핀 불량,접수됨,\n2,어제 21:00,유재석,남자 탈의실,수압이 약해요,조치중,수리 요청함"
}

@st.cache_data(ttl=30)
def fetch_data(url, fallback_key):
    try:
        if "http" in url:
            df = pd.read_csv(url)
            
            # HTML 응답 방어
            if not df.empty and len(df.columns) > 0 and '<html' in str(df.columns[0]).lower():
                raise ValueError("시트 접근 권한 제한됨")

            # 콤마 뭉침 방어
            if len(df.columns) == 1 and ',' in df.columns[0]:
                col_name = df.columns[0]
                raw_text = col_name + '\n' + '\n'.join(df[col_name].astype(str).tolist())
                df = pd.read_csv(io.StringIO(raw_text))
            
            df.columns = df.columns.str.strip()
            df = df.dropna(how='all')
            
            if '티겟분류' in df.columns:
                df.rename(columns={'티겟분류': '타겟분류'}, inplace=True)
                
            return df
    except Exception as e:
        print(f"Fetch Error [{fallback_key}]: {e}")
        pass
    
    # 예외 시 폴백 반환
    fallback_df = pd.read_csv(io.StringIO(FALLBACK_DATA[fallback_key]))
    fallback_df.columns = fallback_df.columns.str.strip()
    return fallback_df

# 데이터 로딩
df_members = fetch_data(SHEET_URL_MEMBER_ANALYTICS, "member")
history_df = fetch_data(SHEET_URL_WORKOUT_HISTORY, "workout")
heatmap_df = fetch_data(SHEET_URL_HEATMAP, "heatmap")
df_qna_init = fetch_data(SHEET_URL_QNA, "qna").fillna("")
df_fac_init = fetch_data(SHEET_URL_FACILITY, "facility").fillna("")

# 타겟별 데이터 분리
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
if 'msg_history' not in st.session_state:
    st.session_state['msg_history'] = []
    
# 상태 초기화
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
        </style>
        """, unsafe_allow_html=True)
        
    elif st.session_state['role'] == 'OWNER':
        st.markdown("""
        <style>
        .stApp { background-color: #F4F7F9; }
        .corp-card { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid #2563EB; margin-bottom: 20px; }
        .stButton>button { background-color: #2563EB !important; color: white !important; border-radius: 8px !important; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 4. 📱 회원 (MEMBER) 앱 화면
# ==========================================
def member_app():
    st.sidebar.markdown(f"**👟 회원 (B2C) 앱 내비게이션**")
    menu = st.sidebar.radio("📋 메뉴 선택", [
        "📊 1. 목표 및 체형 분석",
        "🚀 2. 오늘의 처방 (Today's Fit)", 
        "📡 3. 기구 스캔 (NFC 기록)", 
        "📈 4. 주간 리포트 및 이력", 
        "💬 5. 소통 및 신고함"
    ])

    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<div class='insta-gradient-text'>FITPASS PRO</div>", unsafe_allow_html=True)
        st.markdown("<div class='profile-card'><b>@soomin_workout</b>님, 오늘 하루도 득근하세요! 🔥<br><span style='color:#ccff00;'>보유 포인트: 1,550 P</span></div>", unsafe_allow_html=True)
        
        if menu == "📊 1. 목표 및 체형 분석":
            st.markdown("### 📊 M02. 인바디 업로드 및 목표 설정")
            st.file_uploader("인바디 결과지 (이미지/PDF) 업로드")
            st.selectbox("🎯 최우선 운동 목표", ["근력 증가 (벌크업)", "체중 관리 (다이어트)", "운동 습관 만들기", "재활 및 체형 교정"])
            col1, col2 = st.columns(2)
            with col1: st.number_input("주당 희망 방문 횟수", min_value=1, max_value=7, value=4)
            with col2: st.selectbox("오늘 운동 가능 시간", ["30분", "60분", "90분", "120분"])
            st.multiselect("피하고 싶은 부위 (부상 등)", ["어깨", "허리", "무릎", "손목"], default=["허리"])
            if st.button("목표 저장 및 AI 분석 시작", use_container_width=True): st.toast("목표가 저장되었습니다. AI 트레이너가 루틴을 준비합니다!")

        elif menu == "🚀 2. 오늘의 처방 (Today's Fit)":
            st.markdown("### 🤖 M03. AI 트레이너 오늘의 루틴")
            st.success("🗣 트레이너: '지난번 레그프레스 기록을 훌륭히 소화하셨네요! 최근 하체 볼륨이 부족하니 오늘은 하체 위주로 가볼까요?'")
            st.write("---")
            st.checkbox("🔥 워밍업: 스텝밀(천국의 계단) 10분")
            st.checkbox("💪 메인 1: 파워 랙(스쿼트) 80kg x 10회 (4세트) [직전 동일]")
            st.checkbox("💪 메인 2: 레그 프레스 120kg x 12회 (3세트)")
            st.checkbox("🧘 마무리: 레그 익스텐션 40kg x 15회 (3세트)")
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1: st.button("루틴 건너뛰기 / 변경", use_container_width=True)
            with col2:
                if st.button("💪 운동 시작하기", type="primary", use_container_width=True): st.toast("운동 세션이 시작되었습니다!")

        elif menu == "📡 3. 기구 스캔 (NFC 기록)":
            st.markdown("### 📡 M06. NFC 태그 시뮬레이터")
            machine = st.selectbox("기구를 태그하세요:", ["기구 대기 중...", "파워 랙 (스쿼트)", "벤치프레스 머신", "랫풀다운", "트레드밀 (유산소)"])
            if machine != "기구 대기 중...":
                st.info(f"✅ {machine} 인식 완료")
                if "유산소" in machine:
                    st.write("🏃 웨어러블 심박수 연동 중... (데모 데이터)")
                    st.metric("현재 심박수", "125 bpm")
                    if st.button("유산소 기록 저장", use_container_width=True): st.toast("유산소 기록 완료!")
                else:
                    st.warning("💡 M08. 직전 기록(80kg, 10회)을 불러왔습니다.")
                    c1, c2 = st.columns(2)
                    with c1: weight = st.number_input("중량 (kg)", value=80, step=5)
                    with c2: reps = st.number_input("반복 횟수", value=10, step=1)
                    if st.button("🔊 카운트 시작 (M09A)", use_container_width=True): st.toast("하나! 둘! 잘하고 있어요!")
                    if st.button("💪 이 기록으로 원터치 세트 완료", type="primary", use_container_width=True): st.toast(f"{machine} 1세트 완료! ⏱️ 60초 휴식 타이머 시작.")

        elif menu == "📈 4. 주간 리포트 및 이력":
            st.markdown("### 🏆 M14. 주간 목표 진행률")
            st.progress(0.75, text="주간 방문 목표: 4회 중 3회 완료 (75%)")
            st.markdown("### 📈 M16. 누적 총 볼륨 성장 추이 (스프레드시트 연동)")
            
            if '날짜' in history_df.columns:
                # 🔥 차트 다크 테마 완벽 동기화 및 시인성 극대화
                base = alt.Chart(history_df).encode(
                    x=alt.X('날짜:O', sort=None, axis=alt.Axis(
                        labelAngle=-45, title='날짜', grid=False, 
                        labelColor='white', titleColor='white' # X축 글자 화이트
                    )),
                    y=alt.Y('총 볼륨(kg):Q', scale=alt.Scale(zero=False), axis=alt.Axis(
                        title='총 볼륨(kg)', grid=True, gridColor='rgba(255,255,255,0.2)', 
                        labelColor='white', titleColor='white' # Y축 글자 화이트 및 은은한 그리드
                    )),
                    tooltip=['날짜', '운동 부위', '주요 기구', '총 볼륨(kg)']
                )
                
                area = base.mark_area(
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[alt.GradientStop(color='rgba(0, 242, 254, 0.6)', offset=0), 
                               alt.GradientStop(color='rgba(0, 242, 254, 0.05)', offset=1)],
                        x1=1, x2=1, y1=0, y2=1
                    )
                )
                
                line = base.mark_line(color='#00f2fe', strokeWidth=3, interpolate='monotone')
                
                # 점에 테두리(Stroke)를 주어 배경 묻힘 방지
                points = base.mark_circle(color='#ccff00', size=70, opacity=1, stroke='white', strokeWidth=1)
                
                chart_history = (area + line + points).properties(
                    height=350
                ).configure(
                    background='transparent' # 🔥 배경을 투명하게 날려 다크 CSS 테마와 일체화
                ).configure_view(
                    strokeWidth=0
                ).configure_axis(
                    domainColor='rgba(255,255,255,0.3)',
                    tickColor='rgba(255,255,255,0.3)'
                )
                
                # theme=None 을 명시하여 Streamlit 기본 화이트 테마 강제 해제
                st.altair_chart(chart_history, use_container_width=True, theme=None) 
                
                with st.expander("📝 전체 기록 상세 보기"): st.dataframe(history_df.sort_values(by="날짜", ascending=False), hide_index=True, use_container_width=True)
            else:
                st.warning("데이터 통신 지연: 일시적으로 기록 탭을 불러올 수 없습니다. 권한을 확인해주세요.")
            
            st.info("🗣️ M17. 트레이너 주간 피드백: '이번 주 목표 달성이 눈앞입니다! 지난주 대비 하체 볼륨이 꾸준히 상승했습니다.'")
            if st.button("📸 인스타그램 오운완 스토리 공유", use_container_width=True): st.toast("해시태그가 클립보드에 복사되었습니다.")

        elif menu == "💬 5. 소통 및 신고함":
            tab1, tab2 = st.tabs(["💬 M21. 1:1 질문", "🛠️ M20. 시설 신고"])
            with tab1:
                q_cat = st.selectbox("유형", ["운동 피드백", "PT 문의", "기타"])
                q_text = st.text_area("질문 내용")
                if st.button("질문 전송"): 
                    st.session_state['qna_db'].insert(0, {"id": len(st.session_state['qna_db'])+1, "시간": "방금전", "회원명": "박수민(본인)", "유형": q_cat, "내용": q_text, "상태": "대기중", "답변": ""})
                    st.toast("접수 완료!")
                    st.rerun()
                for i, q in enumerate(st.session_state['qna_db']):
                    with st.expander(f"[{q.get('상태', '대기중')}] {q.get('유형', '')}"): st.write(f"Q: {q.get('내용', '')}\nA: {q.get('답변', '')}")
            with tab2:
                f_loc = st.selectbox("위치", ["프리웨이트존", "유산소존", "탈의실"])
                f_text = st.text_area("신고 내용")
                if st.button("신고 전송"):
                    st.session_state['facility_db'].insert(0, {"id": len(st.session_state['facility_db'])+1, "시간": "방금전", "신고자": "박수민(본인)", "위치": f_loc, "내용": f_text, "상태": "접수됨", "답변": ""})
                    st.toast("신고 접수 완료!")
                    st.rerun()
                for i, f in enumerate(st.session_state['facility_db']):
                    with st.expander(f"[{f.get('상태', '접수됨')}] {f.get('위치', '')}"): st.write(f"{f.get('내용', '')}\n(조치: {f.get('답변', '')})")

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
        if not churn_df.empty and '이탈확률(%)' in churn_df.columns:
            st.altair_chart(alt.Chart(churn_df).mark_bar(color='#2563EB').encode(x=alt.X('이탈확률(%):Q', axis=alt.Axis(title='이탈 확률(%)')), y=alt.Y('회원명:N', sort='-x', axis=alt.Axis(title='회원명')), tooltip=['회원명', '이탈확률(%)']).properties(height=300), use_container_width=True)
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        msg_template = st.text_area("맞춤형 복귀 유도 알림톡 템플릿", "회원님, 최근 방문이 뜸하시네요! 이번 주 오시면 혜택을 드립니다.")
        if st.button("일괄 자동 컨택 발송 (Epic 1-2)", type="primary"): st.toast("이탈 위험군 전체 메시지 발송 완료")

    elif menu == "🏆 Epic 2. 우수 회원 관리":
        st.title("🏆 Epic 2. 우수 회원 자동 선별")
        st.dataframe(vip_df, use_container_width=True, hide_index=True)
        if st.button("🎁 선택 회원 재등록 쿠폰/감사 메시지 발송", type="primary"): st.toast("VIP 혜택 발송 완료")

    elif menu == "🎯 Epic 3. PT 영업 및 성장":
        st.title("🎯 Epic 3. 정체기 회원 타겟팅 (PT 영업)")
        st.dataframe(sales_df, hide_index=True, use_container_width=True)
        if st.button("🎟️ 맞춤형 원포인트 PT 쿠폰 일괄 발송", type="primary"): st.toast("영업 쿠폰 발송 완료")

    elif menu == "💬 Epic 4. Q&A 및 소통":
        st.title("💬 Epic 4. 1:1 질문함 실시간 연동")
        for i, q in enumerate(st.session_state['qna_db']):
            if q.get('상태') == '대기중':
                with st.expander(f"[대기중] {q.get('유형', '')} - {q.get('회원명', '')}", expanded=True):
                    st.write(f"Q. {q.get('내용', '')}")
                    reply = st.text_area("답장 작성", key=f"ans_{i}_{q.get('id', 0)}")
                    if st.button("답장 발송", key=f"btn_{i}_{q.get('id', 0)}", type="primary"):
                        q['상태'] = '답변완료'; q['답변'] = reply; st.rerun()

    elif menu == "🏢 Epic 5. 기구별 혼잡도 분석":
        st.title("🏢 Epic 5. 기구별 맞춤 혼잡도 분석")
        st.write("구글 스프레드시트의 시간대별 점유율 데이터를 기반으로 시각화합니다.")
        machine_columns = [col for col in heatmap_df.columns if col != "시간"]
        selected_machines = st.multiselect("조회할 기구 선택:", options=machine_columns, default=["파워 랙 (웨이트)", "트레드밀 (유산소)"] if len(machine_columns) > 1 else machine_columns)
        if not selected_machines:
            st.warning("조회할 기구를 최소 1개 이상 선택해주세요.")
        elif '시간' in heatmap_df.columns:
            cols_to_keep = ["시간"] + selected_machines
            filtered_df = heatmap_df[cols_to_keep]
            df_melt = filtered_df.melt('시간', var_name='기구', value_name='사용량(%)')
            chart = alt.Chart(df_melt).mark_area(opacity=0.6).encode(
                x=alt.X('시간:O', axis=alt.Axis(labelAngle=0, title='시간대')), 
                y=alt.Y('사용량(%):Q', stack=None, axis=alt.Axis(title='누적 점유율(%)')), 
                color=alt.Color('기구:N', legend=alt.Legend(title="선택된 기구")),
                tooltip=['시간', '기구', '사용량(%)']
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📉 특정 시간대 방문 회원 '오프피크 마케팅' 일괄 발송", type="primary"): 
            st.toast("오프피크 방문 유도 쿠폰이 발송되었습니다.")

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
        st.title("🎉 Epic 8. 기획 이벤트 타겟 홍보")
        st.text_input("이벤트 명", "여름 맞이 바디프로필 챌린지")
        st.selectbox("타겟 필터링", ["전체 회원", "최근 1개월 가입자", "주 3회 이상 출석 VIP"])
        if st.button("이벤트 안내 PUSH 발송", type="primary"): st.toast("이벤트 배포 성공")

    elif menu == "🌱 Epic 9. 신규 회원 정착":
        st.title("🌱 Epic 9. 신규 회원 초기 정착 모니터링")
        onboard_df = pd.DataFrame({"신규 회원명": ["최신규", "이초보"], "가입일": ["D-3", "D-6"], "인바디 등록": ["완료", "미등록"], "첫 방문": ["미방문", "미방문"]})
        st.dataframe(onboard_df, hide_index=True, use_container_width=True)
        if st.button("앱 이용 안내 및 운동 플랜 독려 알림 발송"): st.toast("정착 유도 알림 발송")

    elif menu == "📅 Epic 10. PT 일정 관리":
        st.title("📅 Epic 10. 유휴시간(PT Schedule) 최적화")
        st.info("🕒 오늘 15:00 ~ 16:00 유휴시간 감지됨")
        st.checkbox("추천 행동 1: 정체기 회원(최운식) 원포인트 순회 지도")
        st.checkbox("추천 행동 2: 신규 회원(이초보) 등록 상담 콜")
        if st.button("일정 확정", type="primary"): st.toast("일정에 등록되었습니다.")

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
