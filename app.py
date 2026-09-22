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
        # 회원용: 인스타그램 감성, 트렌디, 다크/그라데이션 톤, 둥근 모서리
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
        # 점주/트레이너용: 깔끔한 엔터프라이즈 대시보드, 직선적, 모노톤+포인트컬러
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
        .metric-container { background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; }
        h1, h2, h3 { color: #2C3E50; font-weight: 700; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 📱 회원 (MEMBER) 앱 화면 - 인스타그램 감성
# ==========================================
def member_app():
    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<h2 class='insta-gradient-text'>✨ Today's Fit</h2>", unsafe_allow_html=True)
        st.markdown("<div class='insta-card'><b>@soomin_workout</b>님, 오늘 하루도 득근하세요! 🔥<br>보유 포인트: 1,500 P</div>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🚀 운동하기", "📸 오운완", "💬 질문하기"])
        
        with tab1:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.subheader("📡 NFC 기구 스캔 (원터치 갱신)")
            st.write("기구에 스마트폰을 태그하여 운동을 기록하세요.")
            
            machine = st.selectbox("가상 NFC 태그:", ["기구를 선택하세요", "벤치프레스 머신 (가슴)"])
            if machine == "벤치프레스 머신 (가슴)":
                # 마찰 관리(Friction Management) 요구사항 반영: 이전 데이터 디폴트 로드
                st.success("✅ 벤치프레스 인식 완료")
                st.info("💡 저번 주에 40kg으로 10회 수행하셨네요! 오늘도 동일하게 세팅해 드릴까요?")
                
                weight = st.number_input("중량 (kg)", value=40, step=5)
                reps = st.number_input("반복 횟수", value=10, step=1)
                
                if st.button("💪 이 기록으로 원터치 세트 완료", use_container_width=True):
                    st.toast("훌륭합니다! 1세트가 기록되었습니다. 🔥")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.subheader("📸 나의 오운완 스토리")
            st.image("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop", caption="#오운완 #스마트헬스장 #하체데이")
            st.write("오늘 소모 칼로리: **450 kcal** | 누적 볼륨: **3,200 kg**")
            st.button("인스타그램으로 바로 공유하기", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab3:
            st.markdown("<div class='insta-card'>", unsafe_allow_html=True)
            st.subheader("🙋‍♂️ 담당 트레이너에게 질문하기")
            st.text_area("운동 중 막히는 부분이 있나요?", placeholder="예: 벤치프레스 할 때 오른쪽 어깨가 살짝 결려요. 자세 문제일까요?")
            if st.button("질문 전송"):
                st.toast("트레이너에게 질문이 전달되었습니다. (평균 응답시간: 1시간 이내)")
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 💻 점주/트레이너 (B2B) 대시보드 - 엔터프라이즈 감성
# ==========================================
def owner_app():
    is_owner = (st.session_state['role'] == 'OWNER')
    role_name = "총괄 점주(관장)" if is_owner else "트레이너(Sub-admin)"
    
    st.sidebar.markdown(f"**접속 계정:** {role_name}")
    
    # RBAC 권한에 따른 메뉴 분리
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

    if menu == "🚨 Epic 1. 이탈 위험 관리":
        st.markdown("<h2>🚨 이탈 위험 신호 자동 감지 보드</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>마지막 방문일로부터 14일 경과 또는 방문 빈도가 50% 이상 급감한 회원을 시스템이 자동 필터링합니다.</div>", unsafe_allow_html=True)
        
        churn_df = pd.DataFrame({
            "회원명": ["김철수", "박지민", "이동국"],
            "위험 사유": ["15일 장기 미방문", "주 4회 ➔ 주 1회 급감", "14일 장기 미방문"],
            "이탈 확률": ["88%", "75%", "82%"],
            "최근 연락": ["-", "7일 전", "-"]
        })
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        
        if st.button("✉️ 선택된 위험 회원에게 '맞춤형 복귀 유도 알림톡' 일괄 발송", type="primary"):
            st.toast("3명의 회원에게 복귀 유도 메시지가 발송되었습니다.")

    elif menu == "🎯 Epic 2. PT 타겟팅 & 성장":
        st.markdown("<h2>🎯 정체기 회원 타겟팅 (PT 영업)</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>3주 이상 주력 기구의 중량 갱신(PR)이 없는 회원을 추출합니다. 원포인트 PT 제안에 최적화된 리스트입니다.</div>", unsafe_allow_html=True)
        
        sales_df = pd.DataFrame({
            "회원명": ["최운식", "정종현", "유재석"],
            "정체 종목": ["벤치프레스", "스쿼트", "데드리프트"],
            "정체 기간": ["4주째 50kg", "3주째 80kg", "5주째 60kg"],
            "운동계획 수행률(목표 달성)": [65, 40, 80] # 프로그레스 바 시각화를 위한 수치
        })
        
        st.dataframe(
            sales_df,
            column_config={
                "운동계획 수행률(목표 달성)": st.column_config.ProgressColumn(
                    "계획 수행률", min_value=0, max_value=100, format="%d%%"
                ),
            },
            hide_index=True, use_container_width=True
        )
        
        if st.button("💪 정체기 회원 '원포인트 PT 제안' 푸시 발송"):
            st.toast("영업 타겟팅 푸시 알림이 전송되었습니다.")

    elif menu == "💬 Epic 3. 트레이너 KPI & 소통":
        st.markdown("<h2>💬 트레이너 소통 및 응답 대시보드</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='corp-card'><b>🤖 시스템 자동 발송 현황 (관장 명의)</b><br>신규 회원 1주차 3회 출석 달성: 이번 주 12건 자동 발송<br>최초 10kg 증량 달성: 이번 주 5건 자동 발송</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='corp-card'><b>📊 트레이너 응답 성과 (KPI)</b><br>평균 응답률: 92%<br>평균 응답 속도: 45분 (목표 60분 이내)</div>", unsafe_allow_html=True)
            
        st.subheader("미해결 회원 질문함")
        qna_df = pd.DataFrame({
            "회원명": ["박수민", "김민지"],
            "질문 내용": ["벤치프레스 할 때 어깨가 아파요.", "인바디 쟀는데 체지방이 안 빠져요."],
            "담당 트레이너": ["강태혁", "이국종"],
            "대기 시간": ["45분", "2시간 10분 ⚠️"]
        })
        st.dataframe(qna_df, hide_index=True, use_container_width=True)

    elif menu == "🏢 Epic 4. 시설 및 오프피크":
        st.markdown("<h2>🏢 기구 혼잡도 히트맵 및 공간 최적화</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>NFC 태그 타임스탬프 기반으로 기구별 하루 점유율을 시각화합니다.</div>", unsafe_allow_html=True)
        
        # 히트맵 데이터를 차트로 시뮬레이션
        heatmap_data = pd.DataFrame({
            "파워 랙 (스쿼트)": [10, 20, 80, 100, 95, 50],
            "랫풀다운": [30, 40, 60, 80, 70, 40],
            "러닝머신": [50, 60, 90, 85, 90, 60]
        }, index=["12:00", "14:00", "18:00", "19:00", "20:00", "22:00"])
        
        st.line_chart(heatmap_data)
        
        st.warning("⚠️ 19:00 ~ 20:00 시간대 파워 랙 점유율이 한계치(100%)에 도달했습니다.")
        if st.button("📉 낮 시간대(14시~16시) 방문 이력 회원 대상 '오프피크 전용 쿠폰' 발송"):
            st.toast("한산한 시간대 방문을 유도하는 타겟 마케팅 쿠폰이 발송되었습니다.")

    elif menu == "🔒 개인정보 및 권한 설정":
        st.markdown("<h2>🔒 Privacy Compliance 및 RBAC 설정</h2>", unsafe_allow_html=True)
        st.markdown("<div class='corp-card'>회원의 개인정보 제공 동의 철회 시 시스템 상에서 민감 정보가 즉각 마스킹(블라인드) 처리됩니다.</div>", unsafe_allow_html=True)
        
        privacy_df = pd.DataFrame({
            "회원명": ["김철수", "박지민 (철회)"],
            "맞춤형 코칭 데이터 활용 동의": ["동의함", "동의 철회"],
            "체중 / 체성분 데이터 열람": ["75kg / 골격근 35kg", "*** / *** (블라인드)"],
            "데이터 보유 기한": ["2028-12-31", "파기 대기"]
        })
        st.dataframe(privacy_df, hide_index=True, use_container_width=True)

    # 트레이너 전용 임시 화면 (RBAC 시뮬레이션)
    elif menu in ["🎯 내 담당 회원 관리", "💬 내 질문함 (응답 대기)"]:
        st.markdown("<h2>트레이너 제한적 접근 화면</h2>", unsafe_allow_html=True)
        st.info("RBAC 보안 정책: 본인에게 할당된 회원의 정보와 질문만 열람할 수 있으며, 헬스장 전체 재무 지표 및 엑셀 다운로드 기능은 차단됩니다.")

# ==========================================
# 🚀 메인 라우팅 (컨트롤 타워)
# ==========================================
def main():
    inject_custom_css() # 동적 CSS 적용
    
    if not st.session_state['logged_in']:
        # 공통 로그인 화면
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
        # 로그인 이후 사이드바 공통 로그아웃 버튼
        if st.sidebar.button("🚪 로그아웃 (권한 변경)"):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.rerun()
            
        # 권한별 앱 분기
        if st.session_state['role'] == 'MEMBER':
            member_app()
        else:
            owner_app()

if __name__ == "__main__":
    main()
