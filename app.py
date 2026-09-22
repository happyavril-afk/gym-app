import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 설정 (반드시 최상단에 위치)
st.set_page_config(page_title="스마트 헬스장 B2B2C", page_icon="⚡", layout="wide")

# 2. 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None

# ==========================================
# 🎨 다이내믹 커스텀 CSS (폰트, 배경, 가독성 개선)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&display=swap');
    @font-face {
        font-family: 'GmarketSans';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff');
        font-weight: 500;
        font-style: normal;
    }
    @font-face {
        font-family: 'GmarketSans';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff') format('woff');
        font-weight: 700;
        font-style: normal;
    }
    
    /* 🌟 기본 텍스트 및 표/그래프(SVG text) 내부 요소 폰트 강제 적용 */
    html, body, [class*="st-"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, 
    [data-testid="stDataFrame"] div, [data-testid="stTable"] th, [data-testid="stTable"] td, 
    svg text, canvas {
        font-family: 'GmarketSans', 'Montserrat', sans-serif !important;
        letter-spacing: -0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state['logged_in']:
        # 🔥 로그인 (첫 페이지): 30대 남녀 에너제틱 짐(Gym) 배경
        st.markdown("""
        <style>
        .stApp {
            background-image: linear-gradient(rgba(10, 10, 12, 0.65), rgba(10, 10, 12, 0.85)), url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .hero-title {
            font-family: 'Montserrat', 'GmarketSans', sans-serif !important;
            font-size: 5.5rem;
            font-weight: 900;
            color: #ffffff;
            text-transform: uppercase;
            text-align: center;
            margin-top: 15vh;
            margin-bottom: 0px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .hero-subtitle {
            font-size: 1.6rem;
            color: #ccff00;
            text-align: center;
            font-weight: 700;
            margin-bottom: 60px;
            text-shadow: 0 2px 10px rgba(204,255,0,0.3);
        }
        .login-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }
        .stButton>button {
            border-radius: 30px !important;
            font-size: 1.6rem !important; 
            font-weight: 900 !important;
            padding: 2.2rem 0 !important; 
            background: transparent !important;
            border: 2px solid #ccff00 !important;
            color: #ccff00 !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            background: #ccff00 !important;
            color: #111 !important;
            box-shadow: 0 0 20px rgba(204,255,0,0.5) !important;
            transform: scale(1.03);
        }
        </style>
        """, unsafe_allow_html=True)

    elif st.session_state['role'] == 'MEMBER':
        # 👟 회원 화면: 다크 & 인스타그램 감성 (가독성 완벽 해결)
        st.markdown("""
        <style>
        .stApp {
            background-color: #0f172a !important; 
            background-image: 
                radial-gradient(at 0% 0%, #1e1b4b 0, transparent 50%), 
                radial-gradient(at 100% 0%, #312e81 0, transparent 50%) !important;
            background-attachment: fixed !important;
        }
        .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
        .stApp span, .stApp label, .stApp div, .stApp b, .stApp li {
            color: #ffffff !important;
        }
        .insta-gradient-text {
            font-family: 'Montserrat', sans-serif !important;
            background: linear-gradient(to right, #00f2fe, #4facfe) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-weight: 900 !important;
            font-size: 2.8rem !important;
            margin-bottom: 15px !important;
            text-align: center !important;
            text-transform: uppercase !important;
        }
        .profile-card {
            background: rgba(255, 255, 255, 0.12) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-radius: 24px !important;
            padding: 25px !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
            margin-bottom: 25px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-radius: 15px !important;
            padding: 8px !important;
            gap: 10px !important;
        }
        .stTabs [data-baseweb="tab"] p { 
            color: #f8fafc !important; 
            font-weight: 700 !important; 
            font-size: 1.2rem !important; 
        }
        .stTabs [aria-selected="true"] { 
            background-color: rgba(204, 255, 0, 0.15) !important; 
            border-radius: 10px !important;
            border: 1px solid rgba(204, 255, 0, 0.4) !important;
        }
        .stTabs [aria-selected="true"] p { 
            color: #ccff00 !important; 
            text-shadow: 0 0 10px rgba(204,255,0,0.5) !important;
        }
        div[data-testid="stAlert"] {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }
        .stButton>button { 
            border-radius: 30px !important; 
            font-weight: 800 !important;
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
            color: #111 !important; 
            border: none !important;
            font-size: 1.2rem !important;
            padding: 1.5rem !important;
        }
        .stSelectbox div[data-baseweb="select"] > div, .stNumberInput div[data-baseweb="input"] > div {
            background-color: rgba(0,0,0,0.4) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
    elif st.session_state['role'] == 'OWNER':
        # 💼 점주 화면: 깔끔하고 화사한 엔터프라이즈 대시보드
        st.markdown("""
        <style>
        .stApp { background-color: #F4F7F9; }
        .corp-card {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
            border-left: 6px solid #2563EB; 
            margin-bottom: 25px;
        }
        h1, h2, h3 { color: #1e293b; font-weight: 900; }
        .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
        .stButton>button { 
            border-radius: 10px !important; 
            font-weight: 800 !important;
            background-color: #2563EB !important;
            color: #fff !important;
            font-size: 1.15rem !important;
            padding: 0.8rem !important;
            border: none !important;
        }
        .stButton>button:hover { background-color: #1D4ED8 !important; }
        div[data-testid="metric-container"] {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
            border: 1px solid #e2e8f0;
        }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 📱 회원 (MEMBER) 앱 화면
# ==========================================
def member_app():
    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<div class='insta-gradient-text'>Today's Fit</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='profile-card'>
            <span style='font-size: 1.2rem;'><b>@soomin_workout</b>님, 오늘 하루도 득근하세요! 🔥</span><br><br>
            <span style='color: #ccff00 !important; font-size: 1.1rem; font-weight: bold;'>보유 포인트: 1,550 P</span>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 오늘의 추천", "📡 기구 태그(NFC)", "📈 과거 이력", "📸 오운완"])
        
        with tab1:
            st.markdown("<h3 style='padding-top: 10px;'>🤖 AI 맞춤 운동 처방</h3>", unsafe_allow_html=True)
            st.info("💡 최근 2주간 하체 볼륨이 상체에 비해 40% 부족합니다. 오늘은 하체(대퇴사두) 중심 루틴을 제안합니다.")
            
            st.checkbox("워밍업: 스텝밀(천국의 계단) 10분")
            st.checkbox("메인 1: 파워 랙(스쿼트) 80kg x 10회 (4세트)")
            st.checkbox("메인 2: 레그 프레스 120kg x 12회 (3세트)")
            st.checkbox("마무리: 레그 익스텐션 40kg x 15회 (3세트)")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💪 운동 시작하기 (워치 심박수 연동)", use_container_width=True):
                st.toast("운동이 시작되었습니다! 부상에 주의하세요.")

        with tab2:
            st.markdown("<h3 style='padding-top: 10px;'>📡 NFC 기구 스캔 (원터치 갱신)</h3>", unsafe_allow_html=True)
            st.write("사용하실 기구에 스마트폰을 태그하세요.")
            
            machine_list = [
                "기구를 선택하세요 (태그 대기 중...)",
                "--- [ 프리웨이트 & 랙 ] ---", "파워 랙 (스쿼트/데드리프트)", "스미스 머신 (전신)", "케이블 크로스오버 (전신)",
                "--- [ 상체 머신 ] ---", "벤치프레스 머신 (가슴)", "펙덱 플라이 (가슴)", "랫풀다운 (등)", "시티드 로우 (등)", "어시스트 풀업 (등)", "숄더 프레스 (어깨)", "사이드 레터럴 레이즈 머신 (어깨)",
                "--- [ 하체 머신 ] ---", "레그 프레스 (하체)", "레그 익스텐션 (앞허벅지)", "레그 컬 (뒷허벅지)", "힙 쓰러스트 머신 (둔근)", "이너타이 / 아웃타이 (허벅지 안/밖)",
                "--- [ 유산소 ] ---", "트레드밀 (러닝머신)", "스텝밀 (천국의 계단)", "실내 사이클 (좌식/입식)", "로잉머신"
            ]
            
            machine = st.selectbox("가상 NFC 태그 시뮬레이터:", machine_list)
            
            if machine != "기구를 선택하세요 (태그 대기 중...)" and not machine.startswith("---"):
                st.success(f"✅ {machine} 인식 완료")
                if "유산소" in machine or "트레드밀" in machine or "스텝밀" in machine or "사이클" in machine or "로잉" in machine:
                    st.info("🏃 유산소 운동은 스마트워치를 통해 심박수와 소모 칼로리가 자동 기록됩니다.")
                    if st.button("유산소 세션 시작", use_container_width=True):
                        st.toast("유산소 기록이 시작되었습니다.")
                else:
                    st.info(f"💡 최근 수행하신 {machine} 기록을 불러왔습니다. 오늘도 동일하게 진행할까요?")
                    col_w, col_r = st.columns(2)
                    with col_w:
                        weight = st.number_input("중량 (kg)", value=50, step=5)
                    with col_r:
                        reps = st.number_input("반복 횟수", value=12, step=1)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💪 이 기록으로 원터치 세트 완료", use_container_width=True):
                        st.toast(f"{machine} {weight}kg x {reps}회 기록 완료! 🔥 휴식 타이머(60초)가 시작됩니다.")
            
        with tab3:
            st.markdown("<h3 style='padding-top: 10px;'>📈 나의 운동 과거 이력</h3>", unsafe_allow_html=True)
            st.write("점진적 과부하 그래프 및 최근 1개월 운동 로그입니다.")
            
            history_data = pd.DataFrame({
                "날짜": ["09.05", "09.08", "09.12", "09.15", "09.18", "09.21"],
                "운동 부위": ["가슴", "하체", "등", "어깨/팔", "가슴", "하체"],
                "주요 기구": ["벤치프레스", "파워 랙", "랫풀다운", "숄더 프레스", "벤치프레스", "레그 프레스"],
                "최고 중량": [45, 70, 40, 25, 50, 80],
                "총 볼륨": [2400, 4200, 2100, 1500, 2800, 4800]
            })
            
            st.markdown("**📊 총 운동 볼륨(kg) 성장 추이**")
            chart_data = history_data.set_index("날짜")[["총 볼륨"]]
            st.line_chart(chart_data)
            
            st.markdown("**📋 상세 기록 로그**")
            st.table(history_data)

        with tab4:
            st.markdown("<h3 style='padding-top: 10px;'>📸 나의 오운완 스토리</h3>", unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop", caption="#오운완 #스마트헬스장 #득근")
            st.write("오늘 소모 칼로리: **450 kcal** | 누적 볼륨: **3,200 kg**")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("인스타그램으로 바로 공유하기", use_container_width=True)

# ==========================================
# 💻 점주 (OWNER) B2B 대시보드 (데이터/시각화 대폭 강화)
# ==========================================
def owner_app():
    st.sidebar.markdown(f"**🏢 총괄 점주(Admin) 대시보드**")
    
    menu = st.sidebar.radio("📋 대시보드 메뉴", [
        "🚨 Epic 1. 이탈 위험 관리", 
        "🎯 Epic 2. PT 타겟팅 & 영업", 
        "💬 Epic 3. AI 소통 & 회원 CS", 
        "🏢 Epic 4. 시설 혼잡도 분석",
        "🔒 Epic 5. 개인정보 동의 현황"
    ])

    if menu == "🚨 Epic 1. 이탈 위험 관리":
        st.title("🚨 이탈 위험 신호 자동 감지 보드")
        
        # 핵심 지표 (Metrics)
        col1, col2, col3 = st.columns(3)
        col1.metric("이번 주 신규 이탈 위험군", "12명", "+3명 🔺")
        col2.metric("AI 예측 이탈 방어 성공률", "68.5%", "4.2% 🔺")
        col3.metric("위험군 전체 복귀 시 예상 매출", "4,200,000원", "-")
        
        st.markdown("<div class='corp-card'>마지막 방문일로부터 14일 경과(조건 A) 또는 방문 빈도가 50% 이상 급감(조건 B)한 회원입니다.</div>", unsafe_allow_html=True)
        
        # 시각화: 요인별 이탈 위험 분포
        st.markdown("**📊 이탈 위험 요인 분포**")
        reason_data = pd.DataFrame({"회원 수": [45, 28, 12]}, index=["장기 미방문 (14일+)", "방문 빈도 급감", "계약 만료 임박"])
        st.bar_chart(reason_data)
        
        # 확장된 데이터프레임
        churn_df = pd.DataFrame({
            "회원명": ["김철수", "박지민", "이동국", "한소희", "마동석", "이지은", "유재석", "강호동", "송지효", "김종국"],
            "위험 사유": [
                "조건 A (18일 미방문)", "조건 B (주 4회➔1회)", "조건 A (24일 미방문)", "조건 B (주 5회➔2회)", 
                "만료 D-5 & 미방문", "조건 A (14일 미방문)", "조건 B (주 3회➔0회)", "조건 A (30일 미방문)", 
                "조건 B (주 2회➔0.5회)", "만료 D-2 & 미방문"
            ],
            "이탈 확률(AI)": ["88%", "75%", "96%", "68%", "92%", "72%", "85%", "99%", "65%", "95%"],
            "회원권 잔여일": ["45일", "120일", "12일", "200일", "5일", "80일", "90일", "3일", "150일", "2일"]
        })
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✉️ 위험군 회원 전체 '복귀유도 맞춤 루틴 템플릿' 카카오 알림톡 자동 전송", use_container_width=True):
            st.toast("10명의 회원에게 메시지가 성공적으로 발송되었습니다.")

    elif menu == "🎯 Epic 2. PT 타겟팅 & 영업":
        st.title("🎯 정체기 회원 타겟팅 (PT 영업 보드)")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("현재 정체기 감지 회원", "24명", "-2명 🔻")
        col2.metric("원포인트 레슨 제안 전환율", "18.2%", "2.1% 🔺")
        col3.metric("이번 달 PT 타겟팅 신규 매출", "12,500,000원", "15% 🔺")

        st.markdown("<div class='corp-card'>특정 주력 기구의 중량/횟수가 최근 3주 이상 갱신(PR)되지 않은 회원입니다. 무료 원포인트 레슨 제안을 통한 PT 전환율이 가장 높은 타겟입니다.</div>", unsafe_allow_html=True)
        
        # 확장된 데이터프레임
        sales_df = pd.DataFrame({
            "회원명": ["최운식", "정종현", "이광수", "전소민", "하동훈", "지석진", "덱스", "기안84", "이시언", "김대호"],
            "정체 종목": ["벤치프레스", "스쿼트", "데드리프트", "숄더 프레스", "레그 프레스", "랫풀다운", "벤치프레스", "스쿼트", "케이블로우", "레그컬"],
            "정체 기간": ["4주째 50kg", "3주째 80kg", "5주째 60kg", "8주째 15kg", "3주째 100kg", "4주째 40kg", "3주째 100kg", "4주째 90kg", "5주째 35kg", "3주째 40kg"],
            "AI 추천 세일즈 액션": ["자세 교정 제안", "보조 운동 제안", "하체 루틴 변경", "유연성 집중 레슨", "고중량 안전 보조", "그립법 변경 제안", "식단 병행 상담", "관절 안정성 레슨", "자극점 찾기 레슨", "햄스트링 집중 레슨"],
            "수행률": [65, 40, 80, 25, 30, 55, 95, 45, 60, 75] 
        })
        
        st.dataframe(
            sales_df,
            column_config={"수행률": st.column_config.ProgressColumn("운동계획 수행률", min_value=0, max_value=100, format="%d%%")},
            hide_index=True, use_container_width=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💪 정체기 회원 전원에게 '무료 원포인트 레슨' 쿠폰 푸시 일괄 발송", use_container_width=True):
            st.toast("타겟팅된 회원들에게 영업 제안이 전송되었습니다.")

    elif menu == "💬 Epic 3. AI 소통 & 회원 CS":
        st.title("💬 AI 자동 소통 및 회원 CS 현황")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("이번 달 AI 자동 축하 발송", "156건", "42건 🔺")
        col2.metric("미해결 CS 질문", "5건", "-")
        col3.metric("CS 평균 응답 시간", "25분", "-5분 🔻 (개선)")
        
        st.markdown("**📈 주간 AI 자동 발송 트렌드 (관장 명의)**")
        msg_data = pd.DataFrame({
            "신규가입 웰컴 메시지": [12, 15, 10, 8, 20, 25, 15],
            "10kg 증량 축하 메시지": [2, 5, 3, 4, 8, 10, 6],
            "출석왕(주 4회) 격려 메시지": [30, 32, 28, 35, 40, 45, 38]
        }, index=["월", "화", "수", "목", "금", "토", "일"])
        st.line_chart(msg_data)
            
        st.markdown("<div class='corp-card'><b>🙋‍♂️ 접수된 회원 질문함 (트레이너 지정 대기)</b></div>", unsafe_allow_html=True)
        
        qna_df = pd.DataFrame({
            "접수 일시": ["오늘 14:20", "오늘 13:05", "어제 20:10", "어제 19:45", "어제 18:30"],
            "회원명": ["박수민", "김민지", "장도연", "양세찬", "박나래"],
            "질문 내용": [
                "벤치프레스 할 때 오른쪽 어깨가 결려요.", 
                "인바디 쟀는데 체지방이 안 빠져요. 식단 문제일까요?", 
                "무릎 수술 이력이 있는데 스쿼트 대체 운동 추천해주세요.", 
                "닭가슴살 말고 단백질 보충제 먹어도 될까요?", 
                "이번 주 일요일은 헬스장 오픈 안 하나요?"
            ],
            "대기 상태": ["🟢 양호 (15분 경과)", "🟡 주의 (2시간 경과)", "🚨 지연 (18시간 경과)", "🚨 지연 (19시간 경과)", "🚨 지연 (20시간 경과)"]
        })
        st.dataframe(qna_df, hide_index=True, use_container_width=True)

    elif menu == "🏢 Epic 4. 시설 혼잡도 분석":
        st.title("🏢 기구 혼잡도(히트맵) 및 공간 최적화")
        
        col1, col2 = st.columns(2)
        col1.metric("최고 혼잡 시간대", "19:00 ~ 20:00", "어제와 동일")
        col2.metric("가장 한산한 시간대(오프피크)", "14:00 ~ 16:00", "-")

        st.markdown("<div class='corp-card'>NFC 태그 타임스탬프 기반 기구별 누적 사용량(Volume) 추이입니다. 면적이 넓을수록 병목이 심한 기구입니다.</div>", unsafe_allow_html=True)
        
        # 누적 사용량을 직관적으로 보여주는 Area Chart 활용
        heatmap_data = pd.DataFrame({
            "파워 랙 (스쿼트)": [15, 30, 45, 55, 80, 100, 95, 85, 60],
            "트레드밀 (유산소)": [40, 50, 70, 65, 95, 90, 80, 75, 60],
            "랫풀다운": [20, 35, 45, 50, 75, 85, 70, 65, 45],
            "스미스 머신": [15, 25, 40, 45, 70, 90, 85, 70, 50],
            "케이블 크로스오버": [25, 30, 50, 55, 65, 80, 75, 60, 40],
            "레그 프레스": [10, 20, 35, 40, 60, 85, 90, 75, 45]
        }, index=["09:00", "11:00", "13:00", "15:00", "17:00", "18:00", "19:00", "20:00", "22:00"])
        
        st.area_chart(heatmap_data)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📉 낮 시간대(13시~16시) 방문 이력 회원군 '오프피크 전용 혜택' 일괄 발송", use_container_width=True):
            st.toast("한산한 시간대 방문을 유도하는 쿠폰이 성공적으로 발송되었습니다.")

    elif menu == "🔒 Epic 5. 개인정보 동의 현황":
        st.title("🔒 Privacy Compliance 및 동의 관리")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("총 활성 회원", "842명", "-")
        col2.metric("마케팅/데이터 활용 동의", "805명", "95.6%")
        col3.metric("최근 7일 동의 철회", "3건", "-")

        st.markdown("<div class='corp-card'>회원의 개인정보 제공 동의 철회 시 시스템 상에서 민감 정보(체성분 등)가 즉각 마스킹(블라인드) 처리되어 법적 리스크를 차단합니다.</div>", unsafe_allow_html=True)
        
        privacy_df = pd.DataFrame({
            "회원명": ["김철수", "박지민 (철회)", "이지은", "마동석", "한소희 (만료)", "유재석", "강호동", "송지효 (철회)"],
            "코칭 데이터 활용 동의": ["동의함 🟢", "동의 철회 🚫", "동의함 🟢", "동의함 🟢", "기간 만료 🚫", "동의함 🟢", "동의함 🟢", "동의 철회 🚫"],
            "체중 / 체성분 데이터 열람": [
                "75.2kg / 골격근 35.1kg", 
                "*** / *** (블라인드 처리)", 
                "52.4kg / 체지방 21%", 
                "105kg / 골격근 50kg", 
                "*** / *** (자동 파기)",
                "68.5kg / 골격근 32kg",
                "115kg / 체지방 25%",
                "*** / *** (블라인드 처리)"
            ],
            "데이터 보유 기한": ["2028-12-31", "파기 대기", "2029-05-15", "2027-10-20", "2026-09-01", "2028-05-01", "2027-11-11", "파기 대기"]
        })
        st.dataframe(privacy_df, hide_index=True, use_container_width=True)

# ==========================================
# 🚀 메인 라우팅 (컨트롤 타워)
# ==========================================
def main():
    inject_custom_css()
    
    if not st.session_state['logged_in']:
        # 🔥 로그인 폼 (권한 2개로 축소 및 레이아웃 최적화)
        st.markdown("<div class='hero-title'>FITPASS PRO</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-subtitle'>스마트 헬스장 데이터 솔루션</div>", unsafe_allow_html=True)
        
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown("<div class='login-card'>", unsafe_allow_html=True)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("👟 회원 (B2C) 접속", use_container_width=True):
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = 'MEMBER'
                    st.rerun()
            with col_b2:
                if st.button("💼 총괄 점주 (B2B) 접속", use_container_width=True):
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = 'OWNER'
                    st.rerun()
                
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.sidebar.button("🚪 시스템 종료 (권한 다시 선택)"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.rerun()
            
        if st.session_state['role'] == 'MEMBER':
            member_app()
        elif st.session_state['role'] == 'OWNER':
            owner_app()

if __name__ == "__main__":
    main()
