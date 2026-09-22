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
# 🎨 동적 CSS 인젝션 (권한별 디자인 완전 분리)
# ==========================================
def inject_custom_css():
    if st.session_state['role'] == 'MEMBER':
        st.markdown("""
        <style>
        .stApp { background-color: #FAFAFA; }
        .insta-card {
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid #eaeaea;
        }
        .insta-gradient-text {
            background: -webkit-linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
        }
        .stButton>button { border-radius: 30px; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)
    elif st.session_state['role'] in ['OWNER', 'TRAINER']:
        st.markdown("""
        <style>
        .stApp { background-color: #F4F6F9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .corp-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #2C3E50;
            margin-bottom: 15px;
        }
        h1, h2, h3 { color: #2C3E50; font-weight: 700; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 📱 회원 (MEMBER) 앱 화면
# ==========================================
def member_app():
    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<h2 class='insta-gradient-text'>✨ Today's Fit</h2>", unsafe_allow_html=True)
        st.markdown("<div class='insta-card'><b>@soomin_workout</b>님, 오늘 하루도 득근하세요! 🔥<br>보유 포인트: 1,550 P</div>", unsafe_allow_html=True)
        
        # 새로운 탭 추가: 과거 이력(History)
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 오늘의 추천", "📡 기구 태그(NFC)", "📈 과거 이력", "📸 오운완"])
        
        with tab1:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.subheader("🤖 AI 맞춤 운동 처방")
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
            st.subheader("📡 NFC 기구 스캔 (원터치 갱신)")
            st.write("사용하실 기구에 스마트폰을 태그하세요.")
            
            # 다양한 기구 리스트업
            machine_list = [
                "기구를 선택하세요 (태그 대기 중...)",
                "--- [ 프리웨이트 & 랙 ] ---",
                "파워 랙 (스쿼트/데드리프트)",
                "스미스 머신 (전신)",
                "케이블 크로스오버 (전신)",
                "--- [ 상체 머신 ] ---",
                "벤치프레스 머신 (가슴)",
                "펙덱 플라이 (가슴)",
                "랫풀다운 (등)",
                "시티드 로우 (등)",
                "어시스트 풀업 (등)",
                "숄더 프레스 (어깨)",
                "사이드 레터럴 레이즈 머신 (어깨)",
                "--- [ 하체 머신 ] ---",
                "레그 프레스 (하체)",
                "레그 익스텐션 (앞허벅지)",
                "레그 컬 (뒷허벅지)",
                "힙 쓰러스트 머신 (둔근)",
                "이너타이 / 아웃타이 (허벅지 안/밖)",
                "--- [ 유산소 ] ---",
                "트레드밀 (러닝머신)",
                "스텝밀 (천국의 계단)",
                "실내 사이클 (좌식/입식)",
                "로잉머신"
            ]
            
            machine = st.selectbox("가상 NFC 태그 시뮬레이터:", machine_list)
            
            if machine != "기구를 선택하세요 (태그 대기 중...)" and not machine.startswith("---"):
                st.success(f"✅ {machine} 인식 완료")
                
                if "유산소" in machine or "트레드밀" in machine or "스텝밀" in machine or "사이클" in machine or "로잉" in machine:
                    st.info("🏃 유산소 운동은 스마트워치를 통해 심박수와 소모 칼로리가 자동 기록됩니다.")
                    if st.button("유산소 세션 시작", use_container_width=True):
                        st.toast("유산소 기록이 시작되었습니다.")
                else:
                    # 근력 운동 원터치 갱신 로직
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
            st.subheader("📈 나의 운동 과거 이력")
            st.write("점진적 과부하 그래프 및 최근 1개월 운동 로그입니다.")
            
            # 과거 운동 이력 목업 데이터
            history_data = pd.DataFrame({
                "날짜": ["09.05", "09.08", "09.12", "09.15", "09.18", "09.21"],
                "운동 부위": ["가슴", "하체", "등", "어깨/팔", "가슴", "하체"],
                "주요 수행 기구": ["벤치프레스 머신", "파워 랙", "랫풀다운", "숄더 프레스", "벤치프레스 머신", "레그 프레스"],
                "최고 중량(kg)": [45, 70, 40, 25, 50, 80], # 중량이 점진적으로 늘어나는 추세
                "총 볼륨(kg)": [2400, 4200, 2100, 1500, 2800, 4800]
            })
            
            # 차트: 총 볼륨 성장 추이 시각화
            st.markdown("**📊 총 운동 볼륨(kg) 성장 추이**")
            chart_data = history_data.set_index("날짜")[["총 볼륨(kg)"]]
            st.line_chart(chart_data)
            
            # 상세 테이블
            st.markdown("**📋 상세 기록 로그**")
            st.dataframe(history_data, hide_index=True, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        with tab4:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.subheader("📸 나의 오운완 스토리")
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
        st.markdown("<div class='corp-card'>14일 미방문 또는 방문 빈도가 50% 이상 급감한 회원 리스트입니다.</div>", unsafe_allow_html=True)
        
        churn_df = pd.DataFrame({
            "회원명": ["김철수", "박지민"],
            "위험 사유": ["15일 장기 미방문", "주 4회 ➔ 주 1회 급감"],
            "이탈 확률": ["88%", "75%"]
        })
        st.dataframe(churn_df, use_container_width=True, hide_index=True)

    elif menu == "🎯 Epic 2. PT 타겟팅 & 성장":
        st.markdown("<h2>🎯 정체기 회원 타겟팅 (PT 영업)</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>3주 이상 주력 기구의 중량 갱신(PR)이 없는 정체기 회원입니다.</div>", unsafe_allow_html=True)
        
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
        st.markdown("<div class='corp-card'>NFC 태그 타임스탬프 기반 기구별 하루 점유율입니다.</div>", unsafe_allow_html=True)
        
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
        st.title("⚡ 스마트 헬스장 플랫폼 로그인")
        st.write("접속할 권한(RBAC)을 선택해주세요.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👟 회원 (B2C)으로 접속", use_container_width=True):
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'MEMBER'
                st.rerun()
        with col2:
            if st.button("💼 총괄 점주 (Admin)로 접속", use_container_width=True):
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'OWNER'
                st.rerun()
        with col3:
            if st.button("💪 일반 트레이너 (Sub-admin)", use_container_width=True):
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'TRAINER'
                st.rerun()
    else:
        if st.sidebar.button("🚪 로그아웃 (권한 변경)"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.rerun()
            
        if st.session_state['role'] == 'MEMBER':
            member_app()
        else:
            owner_app()

if __name__ == "__main__":
    main()
