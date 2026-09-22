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
# 🎨 다이내믹 커스텀 CSS (폰트, 버튼 크기, 캔버스 폰트 강제 적용)
# ==========================================
def inject_custom_css():
    # 🌟 Gmarket Sans & Montserrat 폰트 적용 (그래프, 표 텍스트까지 강제)
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
    /* 기본 텍스트 및 표/그래프 내부 요소 폰트 강제 적용 */
    html, body, [class*="st-"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, 
    [data-testid="stDataFrame"] div, [data-testid="stTable"] th, [data-testid="stTable"] td, text {
        font-family: 'GmarketSans', 'Montserrat', sans-serif !important;
        letter-spacing: -0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state['logged_in']:
        # 🔥 로그인 (첫 페이지): 30대 남녀 에너제틱 배경 & 버튼 크기 확대
        st.markdown("""
        <style>
        .stApp {
            /* 30대 남녀가 함께 운동하는 역동적인 이미지로 교체 */
            background-image: linear-gradient(rgba(10, 10, 12, 0.6), rgba(10, 10, 12, 0.85)), url('https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=2070&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .hero-title {
            font-family: 'Montserrat', 'GmarketSans', sans-serif !important;
            font-size: 5rem;
            font-weight: 900;
            color: #ffffff;
            text-transform: uppercase;
            text-align: center;
            margin-top: 10vh;
            margin-bottom: 0px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .hero-subtitle {
            font-size: 1.6rem;
            color: #ccff00; /* 네온 옐로우그린 */
            text-align: center;
            font-weight: 700;
            margin-bottom: 50px;
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
        /* 로그인 버튼 텍스트 대폭 확대 및 네온 스타일링 */
        .stButton>button {
            border-radius: 30px !important;
            font-size: 1.5rem !important; /* 글자 크기 확대 (기존 1.1rem -> 1.5rem) */
            font-weight: 900 !important;
            padding: 2rem 0 !important; /* 상하 여백 확대하여 버튼 자체를 키움 */
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
        # 👟 회원 화면: 다크 & 글래스모피즘
        st.markdown("""
        <style>
        .stApp {
            background-color: #1a1a24;
            background-image: 
                radial-gradient(at 0% 0%, hsla(253,16%,15%,1) 0, transparent 50%), 
                radial-gradient(at 100% 0%, hsla(225,39%,10%,1) 0, transparent 50%);
        }
        .insta-card {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 24px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            margin-bottom: 25px;
            color: #ffffff;
        }
        .insta-card h2, .insta-card h3, .insta-card p, .insta-card b { color: #ffffff !important; }
        .insta-gradient-text {
            font-family: 'Montserrat', sans-serif !important;
            background: linear-gradient(to right, #00f2fe, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            font-size: 2.8rem;
            margin-bottom: 15px;
            text-align: center;
            text-transform: uppercase;
        }
        .stButton>button { 
            border-radius: 30px !important; 
            font-weight: 800 !important;
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
            color: #111 !important;
            border: none !important;
        }
        .stTabs [data-baseweb="tab"] { color: #aaa !important; font-weight: 700; }
        .stTabs [aria-selected="true"] { color: #fff !important; }
        .stSelectbox label, .stCheckbox label { color: white !important; }
        </style>
        """, unsafe_allow_html=True)
        
    elif st.session_state['role'] in ['OWNER', 'TRAINER']:
        # 💼 점주/트레이너 화면: 시크한 화이트 & 블랙
        st.markdown("""
        <style>
        .stApp { background-color: #F8F9FA; }
        .corp-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
            border-left: 5px solid #111; 
            margin-bottom: 20px;
        }
        h1, h2, h3 { color: #111; font-weight: 800; }
        .stDataFrame { border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .stButton>button { 
            border-radius: 8px !important; 
            font-weight: 700 !important;
            background-color: #111 !important;
            color: #fff !important;
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
        st.markdown("<div class='insta-card'><b>@soomin_workout</b>님, 오늘 하루도 득근하세요! 🔥<br>보유 포인트: 1,550 P</div>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 오늘의 추천", "📡 기구 태그(NFC)", "📈 과거 이력", "📸 오운완"])
        
        with tab1:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.markdown("<h3>🤖 AI 맞춤 운동 처방</h3>", unsafe_allow_html=True)
            st.info("💡 최근 2주간 하체 볼륨이 상체에 비해 40% 부족합니다. 오늘은 하체(대퇴사두) 중심 루틴을 제안합니다.")
            
            st.checkbox("워밍업: 스텝밀(천국의 계단) 10분")
            st.checkbox("메인 1: 파워 랙(스쿼트) 80kg x 10회 (4세트)")
            st.checkbox("메인 2: 레그 프레스 120kg x 12회 (3세트)")
            st.checkbox("마무리: 레그 익스텐션 40kg x 15회 (3세트)")
            
            if st.button("💪 운동 시작하기 (워치 심박수 연동)", use_container_width=True):
                st.toast("운동이 시작되었습니다! 부상에 주의하세요.")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.markdown("<h3>📡 NFC 기구 스캔 (원터치 갱신)</h3>", unsafe_allow_html=True)
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
                    if st.button("💪 이 기록으로 원터치 세트 완료", use_container_width=True):
                        st.toast(f"{machine} {weight}kg x {reps}회 기록 완료! 🔥 휴식 타이머(60초)가 시작됩니다.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab3:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.markdown("<h3>📈 나의 운동 과거 이력</h3>", unsafe_allow_html=True)
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
            # 폰트 강제 적용을 위해 st.table 활용
            st.table(history_data)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab4:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.markdown("<h3>📸 나의 오운완 스토리</h3>", unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop", caption="#오운완 #스마트헬스장 #득근")
            st.write("오늘 소모 칼로리: **450 kcal** | 누적 볼륨: **3,200 kg**")
            st.button("인스타그램으로 바로 공유하기", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 💻 점주/트레이너 (B2B) 대시보드
# ==========================================
def owner_app():
    is_owner = (st.session_state['role'] == 'OWNER')
    role_name = "총괄 점주(관장)" if is_owner else "트레이너(Sub-admin)"
    st.sidebar.markdown(f"**접속 계정:** {role_name}")
    
    if is_owner:
        menu = st.sidebar.radio("📋 대시보드 메뉴", [
            "🚨 Epic 1. 이탈 위험 관리", 
            "🎯 Epic 2. PT 타겟팅 & 성장", 
            "🏢 Epic 3. 시설 및 오프피크"
        ])
    else:
        menu = st.sidebar.radio("📋 대시보드 메뉴", ["🎯 내 담당 회원 관리"])
        st.sidebar.info("💡 Admin 권한 메뉴는 숨김 처리되었습니다.")

    if menu == "🚨 Epic 1. 이탈 위험 관리":
        st.markdown("<h2>🚨 이탈 위험 신호 자동 감지 보드</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>14일 미방문 또는 방문 빈도가 50% 이상 급감한 회원 리스트입니다. 조기 개입으로 이탈률을 획기적으로 낮출 수 있습니다.</div>", unsafe_allow_html=True)
        
        churn_df = pd.DataFrame({
            "회원명": ["김철수", "박지민"],
            "위험 사유": ["15일 장기 미방문", "주 4회 ➔ 주 1회 급감"],
            "이탈 확률": ["88%", "75%"]
        })
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        if st.button("✉️ 위험군 회원 전체 복귀유도 알림톡 자동 발송"):
            st.toast("메시지가 성공적으로 발송되었습니다.")

    elif menu == "🎯 Epic 2. PT 타겟팅 & 성장":
        st.markdown("<h2>🎯 정체기 회원 타겟팅 (PT 영업)</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>3주 이상 주력 기구의 중량 갱신(PR)이 없는 정체기 회원입니다. 원포인트 레슨 제안을 통한 PT 전환율이 가장 높은 타겟입니다.</div>", unsafe_allow_html=True)
        
        sales_df = pd.DataFrame({
            "회원명": ["최운식", "정종현", "유재석"],
            "정체 종목": ["벤치프레스", "스쿼트", "데드리프트"],
            "정체 기간": ["4주째 50kg", "3주째 80kg", "5주째 60kg"],
            "수행률": [65, 40, 80] 
        })
        st.dataframe(
            sales_df,
            column_config={"수행률": st.column_config.ProgressColumn("계획 수행률", min_value=0, max_value=100, format="%d%%")},
            hide_index=True, use_container_width=True
        )

    elif menu == "🏢 Epic 3. 시설 및 오프피크":
        st.markdown("<h2>🏢 기구 혼잡도 히트맵 및 공간 최적화</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>NFC 태그 타임스탬프 기반 기구별 하루 점유율입니다. 병목 시간대를 파악하여 오프피크(Off-peak) 타임 프로모션을 기획하세요.</div>", unsafe_allow_html=True)
        
        heatmap_data = pd.DataFrame({
            "파워 랙 (스쿼트)": [10, 20, 80, 100, 95, 50],
            "랫풀다운": [30, 40, 60, 80, 70, 40]
        }, index=["12:00", "14:00", "18:00", "19:00", "20:00", "22:00"])
        st.line_chart(heatmap_data)

    elif menu == "🎯 내 담당 회원 관리":
        st.markdown("<h2>트레이너 제한적 접근 화면</h2>", unsafe_allow_html=True)

# ==========================================
# 🚀 메인 라우팅 (컨트롤 타워)
# ==========================================
def main():
    inject_custom_css()
    
    if not st.session_state['logged_in']:
        # 🔥 로그인 폼 (히어로 섹션 디자인)
        st.markdown("<div class='hero-title'>FITPASS PRO</div>", unsafe_allow_html=True)
        st.markdown("<div class='hero-subtitle'>스마트 헬스장 데이터 솔루션</div>", unsafe_allow_html=True)
        
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown("<div class='login-card'>", unsafe_allow_html=True)
            
            if st.button("👟 회원 (B2C) 접속", use_container_width=True):
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'MEMBER'
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
                
            if st.button("💼 총괄 점주 (Admin) 접속", use_container_width=True):
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'OWNER'
                st.rerun()
                
            st.markdown("<br>", unsafe_allow_html=True)
                
            if st.button("💪 일반 트레이너 접속", use_container_width=True):
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'TRAINER'
                st.rerun()
                
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.sidebar.button("🚪 시스템 종료 (로그아웃)"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.rerun()
            
        if st.session_state['role'] == 'MEMBER':
            member_app()
        else:
            owner_app()

if __name__ == "__main__":
    main()
