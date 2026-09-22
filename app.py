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
# 🎨 다이내믹 커스텀 CSS (폰트, 배경, 표/그래프 강제 적용)
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
        # 🔥 로그인 (첫 페이지): 30대 남녀 에너제틱 짐(Gym) 배경 & 텍스트 대폭 확대
        st.markdown("""
        <style>
        .stApp {
            /* 30대 남녀가 짐에서 함께 역동적으로 운동하는 고해상도 이미지 */
            background-image: linear-gradient(rgba(10, 10, 12, 0.65), rgba(10, 10, 12, 0.85)), url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop');
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
            color: #ccff00;
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
        /* 버튼 텍스트 및 패딩 대폭 확대 */
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
        # 👟 회원 화면: 다크 & 인스타그램 감성 (글래스모피즘)
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
        # 💼 점주/트레이너 화면: 깔끔하고 사무적인 엔터프라이즈(SaaS) 감성
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
            font-size: 1.1rem !important;
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
                    # 마찰 최소화(Friction Management): 이전 중량 자동 로드 (FRD 요구사항)
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
            st.dataframe(history_data, hide_index=True, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab4:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.markdown("<h3>📸 나의 오운완 스토리</h3>", unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop", caption="#오운완 #스마트헬스장 #득근")
            st.write("오늘 소모 칼로리: **450 kcal** | 누적 볼륨: **3,200 kg**")
            st.button("인스타그램으로 바로 공유하기", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 💻 점주/트레이너 (B2B) 대시보드 (FRD 100% 반영)
# ==========================================
def owner_app():
    is_owner = (st.session_state['role'] == 'OWNER')
    role_name = "총괄 점주(관장)" if is_owner else "트레이너(Sub-admin)"
    st.sidebar.markdown(f"**접속 계정:** {role_name}")
    
    # FRD 요구사항: RBAC에 따른 메뉴 권한 분리[cite: 11]
    if is_owner:
        menu = st.sidebar.radio("📋 대시보드 메뉴", [
            "🚨 Epic 1. 이탈 위험 관리", 
            "🎯 Epic 2. PT 타겟팅 & 성장", 
            "💬 Epic 3. 트레이너 KPI & 소통", 
            "🏢 Epic 4. 시설 및 오프피크",
            "🔒 개인정보 및 권한 설정"
        ])
    else:
        menu = st.sidebar.radio("📋 대시보드 메뉴", ["🎯 내 담당 회원 관리", "💬 내 질문함 (응답 대기)"])
        st.sidebar.info("💡 Admin(점주) 권한 메뉴는 숨김 처리되었습니다.")

    # [FRD 반영] Epic 1: 이탈 위험 신호 자동 감지 및 컨택[cite: 11]
    if menu == "🚨 Epic 1. 이탈 위험 관리":
        st.markdown("<h2>🚨 1-1. 이탈 위험 신호 자동 감지 보드</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>14일 미방문(조건 A) 또는 최근 4주 대비 1주 방문 빈도가 50% 이상 급감(조건 B)한 회원 리스트입니다.<br>🚨 메인 대시보드 배지 알림: <b>오늘 관리가 필요한 이탈 위험 회원 (2명)</b></div>", unsafe_allow_html=True)
        
        churn_df = pd.DataFrame({
            "회원명": ["김철수", "박지민"],
            "위험 사유": ["조건 A (15일 장기 미방문)", "조건 B (주 4회 ➔ 주 1회 급감)"],
            "이탈 확률": ["88%", "75%"]
        })
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        
        st.markdown("<h2>✉️ 1-2. 원클릭 자동 컨택</h2>", unsafe_allow_html=True)
        if st.button("위험군 회원 전체 '복귀유도 맞춤 루틴 템플릿' 카카오 알림톡 전송"):
            st.toast("메시지가 성공적으로 발송되었습니다.")

    # [FRD 반영] Epic 2: PT 타겟팅 (정체기) 및 목표 달성률[cite: 11]
    elif menu == "🎯 Epic 2. PT 타겟팅 & 성장":
        st.markdown("<h2>🎯 2-1. 정체기 회원 타겟팅 (PT 영업 보드)</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>특정 주력 기구의 중량/횟수가 최근 3주 이상 갱신(PR)되지 않은 회원입니다. 원포인트 레슨 제안에 최적화되어 있습니다.</div>", unsafe_allow_html=True)
        
        sales_df = pd.DataFrame({
            "회원명": ["최운식", "정종현", "유재석"],
            "정체 종목": ["벤치프레스 (가슴)", "스쿼트 (하체)", "데드리프트 (등)"],
            "정체 기간": ["4주째 50kg", "3주째 80kg", "5주째 60kg"],
            "수행률": [65, 40, 80] 
        })
        
        # 2-2. 목표 달성률 Progress Bar 시각화 반영[cite: 11]
        st.dataframe(
            sales_df,
            column_config={"수행률": st.column_config.ProgressColumn("운동계획 수행률(목표 달성)", min_value=0, max_value=100, format="%d%%")},
            hide_index=True, use_container_width=True
        )
        if st.button("💪 정체기 회원 '원포인트 PT 제안' 푸시 발송"):
            st.toast("영업 타겟팅 제안이 전송되었습니다.")

    # [FRD 반영] Epic 3: 자동 축하 메시지 및 트레이너 응답 KPI[cite: 11]
    elif menu == "💬 Epic 3. 트레이너 KPI & 소통":
        st.markdown("<h2>💬 트레이너 소통 및 응답 대시보드</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='corp-card'><b>🤖 3-1. 시스템 자동 웰컴/축하 메시지 (관장 명의)</b><br>신규 1주차 3회 출석 달성: 이번 주 12건 자동 발송<br>최초 10kg 증량 달성: 이번 주 5건 자동 발송</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='corp-card'><b>📊 3-2. 트레이너 응답 성과 지표 (KPI)</b><br>평균 질문 응답률: 92%<br>평균 응답 속도: 45분 (목표 KPI: 60분 이내 달성)</div>", unsafe_allow_html=True)
            
        st.subheader("미해결 회원 질문함")
        qna_df = pd.DataFrame({
            "회원명": ["박수민", "김민지"],
            "질문 내용": ["벤치프레스 할 때 어깨가 결려요.", "인바디 쟀는데 체지방이 안 빠져요."],
            "담당 트레이너": ["강태혁", "이국종"],
            "대기 시간": ["45분", "2시간 10분 ⚠️"]
        })
        st.dataframe(qna_df, hide_index=True, use_container_width=True)

    # [FRD 반영] Epic 4: 히트맵 분석 및 오프피크 마케팅[cite: 11]
    elif menu == "🏢 Epic 4. 시설 및 오프피크":
        st.markdown("<h2>🏢 기구 혼잡도 히트맵 및 공간 최적화</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>4-1. NFC 태그 타임스탬프 기반 기구별 하루 점유율(병목 시간대) 시각화입니다.</div>", unsafe_allow_html=True)
        
        heatmap_data = pd.DataFrame({
            "파워 랙 (스쿼트)": [10, 20, 80, 100, 95, 50],
            "랫풀다운": [30, 40, 60, 80, 70, 40]
        }, index=["12:00", "14:00", "18:00", "19:00", "20:00", "22:00"])
        st.line_chart(heatmap_data)
        
        st.markdown("<h2>📉 4-2. 오프피크(Off-peak) 타겟 마케팅</h2>", unsafe_allow_html=True)
        if st.button("낮 시간대(14시~16시) 방문 이력 회원 대상 '오프피크 전용 쿠폰' 일괄 발송"):
            st.toast("한산한 시간대 방문을 유도하는 쿠폰이 발송되었습니다.")

    # [FRD 반영] 시스템 필수 요구사항: 개인정보 동의 관리 (Privacy Compliance)[cite: 11]
    elif menu == "🔒 개인정보 및 권한 설정":
        st.markdown("<h2>🔒 Privacy Compliance 및 동의 관리</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>회원의 개인정보 제공 동의 철회 시 시스템 상에서 민감 정보(체성분 등)가 즉각 마스킹(블라인드) 처리되어 법적 리스크를 차단합니다.</div>", unsafe_allow_html=True)
        
        privacy_df = pd.DataFrame({
            "회원명": ["김철수", "박지민 (철회)"],
            "맞춤형 코칭 데이터 활용 동의": ["동의함", "동의 철회 🚫"],
            "체중 / 체성분 데이터 열람": ["75.2kg / 골격근 35kg", "*** / *** (블라인드 처리)"],
            "데이터 보유 기한": ["2028-12-31", "파기 대기"]
        })
        st.dataframe(privacy_df, hide_index=True, use_container_width=True)

    # 트레이너(Sub-admin) 전용 화면
    elif menu in ["🎯 내 담당 회원 관리", "💬 내 질문함 (응답 대기)"]:
        st.markdown("<h2>트레이너 제한적 접근 화면</h2>", unsafe_allow_html=True)
        st.info("RBAC 보안 정책에 따라 관리자 대시보드(매출, 전체 회원 통계)는 차단되었습니다.")

# ==========================================
# 🚀 메인 라우팅 (컨트롤 타워)
# ==========================================
def main():
    inject_custom_css()
    
    if not st.session_state['logged_in']:
        # 🔥 로그인 폼 (30대 남녀 배경 & 큰 버튼 적용)
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
        if st.sidebar.button("🚪 시스템 종료 (권한 다시 선택)"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.rerun()
            
        if st.session_state['role'] == 'MEMBER':
            member_app()
        else:
            owner_app()

if __name__ == "__main__":
    main()
