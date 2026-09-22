import streamlit as st
import pandas as pd
import datetime

# 1. 페이지 및 상태 초기화
st.set_page_config(page_title="스마트 헬스장 (B2B2C)", page_icon="⚡", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
if 'member_points' not in st.session_state:
    st.session_state['member_points'] = 1500

# 2. 로그인 화면 (B2B2C 권한 분기)
def login_screen():
    st.title("⚡ FitPass Open - 스마트 헬스장 B2B2C 플랫폼")
    st.markdown("하나의 플랫폼에서 회원(B2C)과 점주(B2B)가 어떻게 상호작용하는지 확인하세요.")
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📱 회원 (Member) 모드")
        st.write("스마트워치 데이터와 NFC 태깅을 통해 PT처럼 관리받는 경험을 제공합니다.")
        if st.button("회원 앱으로 접속하기", use_container_width=True):
            st.session_state['logged_in'] = True
            st.session_state['role'] = 'MEMBER'
            st.rerun()
            
    with col2:
        st.subheader("💻 점주 (Owner) 모드")
        st.write("회원의 행동 데이터를 분석하여 이탈을 방지하고 PT 매출을 극대화합니다.")
        if st.button("점주 대시보드로 접속하기", type="primary", use_container_width=True):
            st.session_state['logged_in'] = True
            st.session_state['role'] = 'OWNER'
            st.rerun()

# 3. 회원(Member) 사이드 UX
def member_app():
    # 모바일 앱 느낌을 주기 위해 중앙 컬럼만 사용
    _, col_main, _ = st.columns([1, 2, 1])
    
    with col_main:
        st.title("👋 안녕하세요, 박수민 회원님!")
        st.write(f"보유 포인트: **{st.session_state['member_points']} P**")
        
        # 탭 구성: 오늘 운동 / NFC 연동 / 내 성과
        tab1, tab2, tab3 = st.tabs(["🎯 오늘의 추천", "📡 기구 태그(NFC)", "🏆 내 성과 및 랭킹"])
        
        with tab1:
            st.subheader("AI 맞춤 운동 처방")
            st.info("💡 어제는 하체 운동(볼륨 3,200kg)을 강도 높게 수행하셨네요. 오늘은 상체 회복 루틴을 추천합니다!")
            
            # 루틴 체크리스트 시뮬레이션
            st.checkbox("워밍업: 러닝머신 15분 (심박수 120 유지)")
            st.checkbox("메인 1: 체스트 프레스 30kg x 12회 (3세트)")
            st.checkbox("메인 2: 랫풀다운 25kg x 15회 (3세트)")
            
            if st.button("💪 운동 시작하기", use_container_width=True):
                st.toast("웨어러블 심박수 연동이 시작되었습니다!")
                
        with tab2:
            st.subheader("기구 스캔 및 가이드")
            st.markdown("기구에 부착된 NFC 스티커에 스마트폰을 태그하세요.")
            
            machine = st.selectbox("가상 NFC 스캔 시뮬레이션:", ["선택하세요", "체스트 프레스 머신", "파워 랙 (스쿼트)"])
            
            if machine == "체스트 프레스 머신":
                st.success("✅ 체스트 프레스 머신 인식 완료")
                st.video("https://www.youtube.com/watch?v=Gji3G-e66-w") # 임시 유튜브 링크
                st.metric(label="회원님 체형(175cm) 맞춤 의자 세팅", value="3칸 높이기")
                st.metric(label="오늘의 추천 중량", value="30 kg")
                
                if st.button("세트 완료 및 기록 저장"):
                    st.toast("성공적으로 기록되었습니다! 휴식 시간(60초)을 셉니다.")
                    st.session_state['member_points'] += 50
                    
            elif machine == "파워 랙 (스쿼트)":
                st.error("🚨 현재 해당 기구는 다른 회원이 사용 중입니다. (혼잡도 높음)")
                st.warning("대체 기구 안내: 빈 기구인 '레그 프레스 머신'으로 하체 운동을 대체하시겠습니까?")
                if st.button("대체 기구 위치 확인하기"):
                    st.toast("지도에 레그 프레스 머신 위치가 표시됩니다.")

        with tab3:
            st.subheader("이번 주 성과 및 랭킹")
            col_a, col_b = st.columns(2)
            col_a.metric("주간 누적 볼륨", "8,500 kg", "15% 🔺")
            col_b.metric("소모 칼로리", "1,240 kcal", "2% 🔻")
            
            st.divider()
            st.markdown("#### 🥇 우리 동네 헬스장 익명 리더보드")
            leaderboard = pd.DataFrame({
                "순위": ["1위", "2위", "3위 (Me)"],
                "닉네임": ["근육짱짱맨", "운동하는직장인", "박수민 (본인)"],
                "이번주 출석": ["5일", "4일", "3일"]
            })
            st.dataframe(leaderboard, hide_index=True, use_container_width=True)
            
            if st.button("📸 인스타 스토리용 오운완 카드 생성", use_container_width=True):
                st.success("운동 볼륨과 칼로리가 예쁘게 디자인된 이미지가 갤러리에 저장되었습니다!")

# 4. 점주(Owner) 사이드 UX
def owner_app():
    st.sidebar.title("🏢 점주 관리자 패널")
    menu = st.sidebar.radio("메뉴 이동", ["📊 전체 운영 통계", "🎯 PT 영업 타겟팅 보드", "⚙️ 기구 병목 및 챌린지"])
    
    if menu == "📊 전체 운영 통계":
        st.title("지점 운영 통합 대시보드")
        col1, col2, col3 = st.columns(3)
        col1.metric("활성 회원 수", "412명", "12명 신규 🔺")
        col2.metric("이달의 예상 이탈률", "4.2%", "0.8% 🔻")
        col3.metric("최근 7일 출석률", "68%", "5% 🔺")
        
        st.subheader("주간 요일별 출석 트렌드 (웨어러블/NFC 데이터 기반)")
        chart_data = pd.DataFrame({'출석 인원': [120, 150, 180, 140, 110, 90, 85]}, 
                                  index=['월', '화', '수', '목', '금', '토', '일'])
        st.bar_chart(chart_data)
        
    elif menu == "🎯 PT 영업 타겟팅 보드":
        st.title("🚨 정체기 및 이탈 위험 회원 리스트")
        st.markdown("회원의 성장 정체기와 방문율 하락 데이터를 AI가 분석하여 조기 개입 타이밍을 제안합니다.")
        
        risk_data = pd.DataFrame({
            "회원명": ["김현철", "최운식", "정종현", "장은진"],
            "상태 분류": ["🔴 이탈 위험 (3주 미방문)", "🟡 중량 정체기 (4주째 벤치프레스 동일)", "🟡 체성분 목표 미달", "🟢 양호"],
            "AI 추천 개입 액션": ["복귀 유도 쿠폰 (알림톡 발송)", "원포인트 PT 레슨 무료 제안", "루틴 변경 상담 (전화)", "자동 축하 메시지 발송"]
        })
        st.dataframe(risk_data, use_container_width=True, hide_index=True)
        
        st.divider()
        col_x, col_y = st.columns(2)
        with col_x:
            if st.button("🔴 이탈 위험군 전체 '복귀 유도 쿠폰' 자동 발송"):
                st.toast("김현철 회원 외 4명에게 7일 연장 쿠폰 알림톡이 발송되었습니다!")
        with col_y:
            if st.button("🟡 정체기 회원 전체 '원포인트 PT' 영업 알림 발송"):
                st.toast("최운식 회원 외 8명에게 무료 자세교정 쿠폰이 발송되었습니다!")

    elif menu == "⚙️ 기구 병목 및 챌린지":
        st.title("공간 최적화 및 커뮤니티 관리")
        
        st.subheader("🔥 시간대별 기구 NFC 점유율 (히트맵 분석)")
        st.write("저녁 7시~8시 파워 랙 점유율이 95%에 달하여 회원 불만이 예상됩니다. 오전 타임 마케팅을 전개하세요.")
        
        if st.button("낮 시간대(12~16시) 방문 가능 회원 대상 타임 쿠폰 발송"):
            st.toast("타겟팅된 회원 120명에게 발송 완료!")
            
        st.divider()
        st.subheader("🏆 헬스장 자체 커스텀 챌린지 생성")
        ch_name = st.text_input("챌린지 이름", "10월 한 달 20일 출석왕 도전!")
        ch_reward = st.text_input("목표 달성 보상", "개인 락커 1개월 무료 이용권")
        if st.button("챌린지 회원 앱에 게시하기", type="primary"):
            st.success(f"[{ch_name}] 챌린지가 모든 회원 앱 메인 화면에 노출되었습니다.")

# 5. 메인 컨트롤러
if not st.session_state['logged_in']:
    login_screen()
else:
    st.sidebar.markdown(f"**현재 모드:** `{'점주(B2B)' if st.session_state['role'] == 'OWNER' else '회원(B2C)'}`")
    if st.sidebar.button("로그아웃 (권한 변경)"):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.rerun()
        
    if st.session_state['role'] == 'MEMBER':
        member_app()
    elif st.session_state['role'] == 'OWNER':
        owner_app()
