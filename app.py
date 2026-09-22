import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="스마트 헬스장 대시보드", page_icon="💪", layout="wide")

# 2. 세션 상태 초기화 (RBAC 권한 관리)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None

# 3. 로그인 화면 (시연용으로 비밀번호 없이 버튼 클릭으로 분기)
def login_screen():
    st.title("💪 스마트 헬스장 B2B 대시보드 (프로토타입)")
    st.markdown("수업 시연용 화면입니다. 접속할 계정의 권한(Role)을 선택해주세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("👨‍💼 점주(Owner) 계정: 전체 통계, 이탈 예측, 환불 관리")
        if st.button("점주 권한으로 접속하기"):
            st.session_state['logged_in'] = True
            st.session_state['role'] = 'OWNER'
            st.rerun()
    
    with col2:
        st.success("🏋️‍♂️ 트레이너(Trainer) 계정: 내 일정, 정산 내역 (전체 회원 열람 불가)")
        if st.button("트레이너 권한으로 접속하기"):
            st.session_state['logged_in'] = True
            st.session_state['role'] = 'TRAINER'
            st.rerun()

# 4. 점주(Owner) 전용 화면
def owner_dashboard():
    st.sidebar.title("👨‍💼 점주 전용 메뉴")
    menu = st.sidebar.radio("메뉴 이동", ["📊 전체 대시보드", "🚨 ML 이탈 위험 관리", "💰 법정 환불 계산기"])
    
    if menu == "📊 전체 대시보드":
        st.header("전체 지점 재무 및 운영 통계")
        col1, col2, col3 = st.columns(3)
        col1.metric("이번 달 총 매출", "45,000,000원", "12% 🔺")
        col2.metric("활성 회원 수", "342명", "5명 🔻")
        col3.metric("금주 PT 진행 횟수", "128회", "8회 🔺")
        
    elif menu == "🚨 ML 이탈 위험 관리":
        st.header("XGBoost 이탈 예측 타겟 리스트")
        st.markdown("머신러닝 모델이 최근 4주간의 방문 패턴을 분석하여 이탈 확률이 높은 회원을 사전 추출합니다.")
        
        # 시연용 가상 데이터
        data = {
            '회원명': ['김철수', '이영희', '박지민', '최동석'],
            '잔여기간': ['15일', '40일', '10일', '60일'],
            '주간 방문빈도 변화': ['주 4회 ➡️ 1회', '주 3회 ➡️ 2회', '주 2회 ➡️ 0회', '주 5회 ➡️ 4회'],
            '이탈 확률(ML 스코어)': ['88% (위험)', '65% (주의)', '92% (매우 위험)', '20% (안전)']
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        if st.button("위험군(80% 이상) 전체에게 타겟 알림톡 발송"):
            st.toast("✅ 김철수, 박지민 회원에게 재방문 유도 쿠폰 알림톡이 발송되었습니다!")
        
    elif menu == "💰 법정 환불 계산기":
        st.header("소비자원 기준 환불 자동 산출 (PT 횟수제 기준)")
        st.markdown("복잡한 위약금과 기이용 금액을 법적 기준에 맞춰 단 1초 만에 자동 계산하여 분쟁을 차단합니다.")
        
        total_price = st.number_input("총 결제 금액 (원)", min_value=0, value=1000000, step=10000)
        total_pt = st.number_input("총 계약 PT 횟수 (회)", min_value=1, value=20)
        used_pt = st.number_input("이용 완료 PT 횟수 (회)", min_value=0, value=5)
        
        is_valid_reason = st.checkbox("정당한 사유 (질병, 이사 등) 여부 - 체크 시 10% 위약금 면제")
        
        if st.button("환불액 자동 계산하기"):
            price_per_pt = total_price / total_pt
            used_amount = price_per_pt * used_pt
            penalty = 0 if is_valid_reason else total_price * 0.1
            refund_amount = total_price - used_amount - penalty
            
            st.divider()
            st.subheader("🧾 계산 결과 (대법원 및 소비자원 가이드라인 적용)")
            st.write(f"- 기이용 금액 ({used_pt}회 진행): **{int(used_amount):,}원**")
            st.write(f"- 위약금 (총 결제액의 10%): **{int(penalty):,}원**")
            st.markdown(f"### ➡️ 최종 환불 지급액: **<span style='color:blue'>{int(max(0, refund_amount)):,}원</span>**", unsafe_allow_html=True)

# 5. 트레이너(Trainer) 전용 화면
def trainer_dashboard():
    st.sidebar.title("🏋️‍♂️ 트레이너 전용 메뉴")
    menu = st.sidebar.radio("메뉴 이동", ["📅 내 PT 일정 및 출석", "💸 급여 및 환수(Clawback) 내역"])
    
    if menu == "📅 내 PT 일정 및 출석":
        st.header("오늘의 담당 회원 수업")
        st.info("보안 정책(RBAC): 본인에게 할당된 PT 회원의 정보만 제한적으로 열람할 수 있습니다. (전체 엑셀 다운로드 차단)")
        st.success("14:00 - 김철수 회원 (하체 / 스쿼트 80kg 진행 예정)")
        st.success("16:30 - 이영희 회원 (상체 / 라운드숄더 교정)")
        
        if st.button("✅ 14:00 김철수 회원 수업 완료 처리 (GPS 인증 시뮬레이션)"):
            st.toast("현재 위치가 헬스장 내부(반경 50m)로 확인되어 수업 출석이 증빙되었습니다!")
            
    elif menu == "💸 급여 및 환수(Clawback) 내역":
        st.header("당월 정산 내역 투명화")
        st.metric("현재까지 누적 예상 급여 (세션 수수료)", "1,850,000원")
        
        st.divider()
        st.subheader("🚨 수수료 환수(Clawback) 발생 내역")
        st.error("박지민 회원 (PT 10회 중 2회 진행 후 중도 환불) \n\n기지급된 커미션 중 미진행 분에 대해 80,000원이 익월 급여에서 공제(환수)될 예정입니다.")

# 6. 메인 앱 실행 흐름 (컨트롤 타워)
if not st.session_state['logged_in']:
    login_screen()
else:
    # 사이드바 하단에 로그인 정보 표시
    st.sidebar.divider()
    st.sidebar.markdown(f"**현재 접속 권한:** `{st.session_state['role']}`")
    
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.rerun()
        
    # 권한에 따른 화면 노출
    if st.session_state['role'] == 'OWNER':
        owner_dashboard()
    elif st.session_state['role'] == 'TRAINER':
        trainer_dashboard()