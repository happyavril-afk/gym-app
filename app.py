import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# ==========================================
# 1. 💾 대규모 풍부한 시뮬레이션 데이터 로드
# ==========================================
def load_mock_data():
    history_df = pd.DataFrame({
        "날짜": ["07.01", "07.03", "07.05", "07.08", "07.10", "07.14", "07.18", "07.22", "07.25", "07.28", 
                 "08.02", "08.05", "08.10", "08.13", "08.15", "08.20", "08.22", "08.25", "08.28", "09.01", 
                 "09.03", "09.05", "09.08", "09.12", "09.15", "09.18", "09.20", "09.21"],
        "운동 부위": ["가슴", "하체", "등", "어깨", "가슴", "하체", "등", "어깨", "하체", "가슴", 
                  "하체", "등", "어깨", "가슴", "가슴", "하체", "전신", "등", "가슴", "등", 
                  "하체", "가슴", "하체", "등", "어깨", "가슴", "전신", "하체"],
        "주요 기구": ["벤치프레스", "스쿼트", "랫풀다운", "밀리터리 프레스", "벤치프레스", "레그 프레스", "시티드 로우", "숄더 프레스", "런지", "체스트 프레스", 
                  "레그 익스텐션", "풀업", "사이드 레터럴 레이즈", "인클라인 벤치", "벤치프레스", "스쿼트", "케이블 크로스오버", "바벨 로우", "펙덱 플라이", "풀업", 
                  "레그 프레스", "벤치프레스", "파워 랙", "랫풀다운", "숄더 프레스", "벤치프레스", "케이블", "레그 프레스"],
        "총 볼륨(kg)": [1800, 2100, 1900, 1200, 1950, 2200, 2050, 1300, 2100, 2000, 
                     2300, 2100, 1400, 2200, 2100, 2500, 1800, 2400, 2300, 2100, 
                     2700, 2400, 3200, 2100, 1500, 2800, 2000, 3800]
    })
    
    churn_df = pd.DataFrame({
        "회원명": ["김철수", "박지민", "이동국", "한소희", "마동석", "정우성", "이지은", "최우식"],
        "위험 사유": ["18일 미방문", "방문 주 4회➔1회", "24일 미방문", "PT 종료 후 미방문", "만료 D-5 & 미방문", "방문 시간대 불규칙", "최근 2주 볼륨 급감", "30일 장기 미방문"],
        "이탈 확률(%)": [88, 75, 96, 68, 92, 55, 62, 99],
        "회원권 잔여일": [45, 120, 12, 200, 5, 80, 150, 3]
    })
    
    vip_df = pd.DataFrame({
        "회원명": ["이광수", "유재석", "송지효", "김종국", "하동훈", "양세찬"],
        "주 평균 방문": [4.5, 3.2, 5.1, 6.5, 3.8, 4.0],
        "볼륨 증감률(%)": [12, 5, 22, 35, 8, 15],
        "가입 기간(개월)": [14, 8, 24, 48, 12, 6],
        "최근 응답": ["긍정적", "보통", "매우 긍정", "긍정적", "보통", "긍정적"]
    })
    
    sales_df = pd.DataFrame({
        "회원명": ["최운식", "전소민", "조세호", "남창희", "김숙"],
        "정체 종목": ["스쿼트", "숄더 프레스", "데드리프트", "벤치프레스", "랫풀다운"],
        "정체 기간(주)": [4, 3, 6, 3, 5],
        "중량(kg)": [80, 15, 100, 65, 30],
        "수행률(%)": [65, 40, 80, 25, 45],
        "AI 추천 영업": ["자세 교정 제안", "보조 운동 제안", "하체 루틴 변경", "안전 보조", "그립 교정 레슨"]
    })
    
    hours = ["06:00", "09:00", "12:00", "15:00", "18:00", "19:00", "20:00", "22:00"]
    heatmap_df = pd.DataFrame({
        "시간": hours,
        "파워 랙 (웨이트)": [5, 15, 25, 45, 80, 100, 95, 60],
        "트레드밀 (유산소)": [10, 40, 30, 65, 95, 90, 80, 60],
        "스미스 머신": [2, 10, 20, 35, 75, 85, 70, 45],
        "스트레칭존": [5, 10, 15, 20, 40, 50, 45, 20],
        "케이블 머신": [8, 20, 35, 50, 85, 95, 80, 50]
    })
    
    return history_df, churn_df, vip_df, sales_df, heatmap_df

# ==========================================
# 2. 페이지 및 세션 상태 초기화
# ==========================================
st.set_page_config(page_title="FITPASS PRO", page_icon="⚡", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
if 'msg_history' not in st.session_state:
    st.session_state['msg_history'] = []
if 'qna_db' not in st.session_state:
    st.session_state['qna_db'] = [
        {"id": 1, "시간": "오늘 14:20", "회원명": "박수민", "유형": "🏋️ 운동/자세 피드백", "내용": "벤치프레스 할 때 오른쪽 어깨가 결려요.", "상태": "대기중", "답변": ""},
        {"id": 2, "시간": "오늘 13:05", "회원명": "김민지", "유형": "💳 회원권/PT 문의", "내용": "PT 10회 추가 결제 할인 문의", "상태": "답변완료", "답변": "네, 10% 추가 할인 적용됩니다!"},
        {"id": 3, "시간": "어제 19:30", "회원명": "장동건", "유형": "💡 기타", "내용": "주차 등록은 어디서 하나요?", "상태": "답변완료", "답변": "인포데스크 태블릿에서 차량번호 4자리 입력하시면 3시간 무료입니다."}
    ]
if 'facility_db' not in st.session_state:
    st.session_state['facility_db'] = [
        {"id": 1, "시간": "오늘 09:15", "신고자": "이동국", "위치": "프리웨이트존", "내용": "인클라인 벤치 각도 조절 핀 불량", "상태": "접수됨", "답변": ""},
        {"id": 2, "시간": "어제 21:00", "신고자": "유재석", "위치": "남자 탈의실", "내용": "안쪽 샤워기 수압이 너무 약해요", "상태": "조치중", "답변": "관리소에 수리 요청했습니다."},
        {"id": 3, "시간": "어제 14:20", "신고자": "송지효", "위치": "유산소존", "내용": "3번 러닝머신 덜컹거림", "상태": "조치완료", "답변": "수평 조절 나사 재조정 완료했습니다."}
    ]

history_df, churn_df, vip_df, sales_df, heatmap_df = load_mock_data()

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
        .stApp { background-image: linear-gradient(rgba(10, 10, 12, 0.65), rgba(10, 10, 12, 0.85)), url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop'); background-size: cover; background-position: center; }
        .hero-title { font-family: 'Montserrat', sans-serif !important; font-size: clamp(2.5rem, 10vw, 5.5rem) !important; font-weight: 900; color: #ffffff; text-align: center; margin-top: 15vh; white-space: nowrap; }
        .hero-subtitle { font-size: clamp(1rem, 4vw, 1.6rem) !important; color: #ccff00; text-align: center; font-weight: 700; margin-bottom: 60px; }
        .login-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); border-radius: 20px; padding: clamp(20px, 5vw, 40px); }
        .stButton>button { border-radius: 30px !important; font-weight: 900 !important; border: 2px solid #ccff00 !important; color: #ccff00 !important; background: transparent !important; }
        .stButton>button:hover { background: #ccff00 !important; color: #111 !important; }
        </style>
        """, unsafe_allow_html=True)

    elif st.session_state['role'] == 'MEMBER':
        st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; }
        [data-testid="stMain"] p, [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3, [data-testid="stMain"] span:not([class*="stIcon"]):not(.material-icons), [data-testid="stMain"] label, [data-testid="stMain"] li { color: #ffffff !important; }
        .insta-gradient-text { font-family: 'Montserrat', sans-serif !important; background: linear-gradient(to right, #00f2fe, #4facfe) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-weight: 900 !important; font-size: 2.5rem !important; text-align: center !important; }
        .profile-card { background: rgba(255, 255, 255, 0.1) !important; border-radius: 24px !important; padding: 20px !important; margin-bottom: 20px !important; }
        .stButton>button { border-radius: 20px !important; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important; color: #111 !important; border: none !important; font-weight: 800 !important; }
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
            st.info("신규 회원의 인바디를 분석하고 주간 목표를 설정합니다.")
            st.file_uploader("인바디 결과지 (이미지/PDF) 업로드")
            st.selectbox("🎯 최우선 운동 목표", ["근력 증가 (벌크업)", "체중 관리 (다이어트)", "운동 습관 만들기", "재활 및 체형 교정"])
            col1, col2 = st.columns(2)
            with col1: st.number_input("주당 희망 방문 횟수", min_value=1, max_value=7, value=4)
            with col2: st.selectbox("오늘 운동 가능 시간", ["30분", "60분", "90분", "120분"])
            st.multiselect("피하고 싶은 부위 (부상 등)", ["어깨", "허리", "무릎", "손목"], default=["허리"])
            if st.button("목표 저장 및 AI 분석 시작", use_container_width=True): st.toast("목표가 저장되었습니다. AI 트레이너가 루틴을 준비합니다!")

        elif menu == "🚀 2. 오늘의 처방 (Today's Fit)":
            st.markdown("### 🤖 M03. AI 트레이너 오늘의 루틴")
            st.success("🗣️ 트레이너: '지난번 레그프레스 10회를 훌륭히 소화하셨네요! 최근 하체 볼륨이 부족하니 오늘은 하체 위주로 가볼까요?'")
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
            st.markdown("### 📈 M16. 2개월간 총 볼륨 성장 추이")
            chart_history = alt.Chart(history_df).mark_line(point=True, color='#00f2fe').encode(
                x=alt.X('날짜:O', sort=None, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('총 볼륨(kg):Q', scale=alt.Scale(zero=False)),
                tooltip=['날짜', '운동 부위', '주요 기구', '총 볼륨(kg)']
            ).properties(height=300)
            st.altair_chart(chart_history, use_container_width=True)
            with st.expander("📝 전체 기록 상세 보기"): st.dataframe(history_df.sort_values(by="날짜", ascending=False), hide_index=True, use_container_width=True)
            st.info("🗣️ M17. 트레이너 주간 피드백: '이번 주 목표 달성이 눈앞입니다! 지난주 대비 하체 볼륨이 15% 상승했습니다.'")
            if st.button("📸 인스타그램 오운완 스토리 공유", use_container_width=True): st.toast("해시태그가 클립보드에 복사되었습니다.")

        elif menu == "💬 5. 소통 및 신고함":
            tab1, tab2 = st.tabs(["💬 M21. 1:1 질문", "🛠️ M20. 시설 신고"])
            with tab1:
                q_cat = st.selectbox("유형", ["운동 피드백", "PT 문의", "기타"])
                q_text = st.text_area("질문 내용")
                if st.button("질문 전송"): st.toast("접수 완료!")
                for q in st.session_state['qna_db']:
                    with st.expander(f"[{q['상태']}] {q['유형']}"): st.write(f"Q: {q['내용']}\nA: {q['답변']}")
            with tab2:
                f_loc = st.selectbox("위치", ["프리웨이트존", "유산소존", "탈의실"])
                f_text = st.text_area("신고 내용")
                if st.button("신고 전송"): st.toast("신고 접수 완료!")
                for f in st.session_state['facility_db']:
                    with st.expander(f"[{f['상태']}] {f['위치']}"): st.write(f"{f['내용']}\n(조치: {f['답변']})")

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
        "🏢 Epic 5. 기구별 혼잡도 분석",  # 💡 업데이트된 메뉴명
        "🔒 Epic 6. 개인정보 동의",
        "🛠️ Epic 7. 시설 민원 관리",
        "🎉 Epic 8. 이벤트 홍보",
        "🌱 Epic 9. 신규 회원 정착",
        "📅 Epic 10. PT 일정 관리"
    ])

    if menu == "🏠 Epic 0. 오늘의 할 일 홈":
        st.title("🏠 Epic 0. 오늘의 할 일 홈 화면")
        st.markdown("<div class='corp-card'>점주님이 오늘 당장 처리해야 할 핵심 업무 현황을 요약합니다.</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("🚨 신규 이탈 위험군", f"{len(churn_df)}명", "조치 필요")
        c2.metric("💬 미답변 1:1 질문", "1건", "대기중")
        c3.metric("🛠️ 신규 시설 민원", "1건", "확인 요망")
        c4, c5, c6 = st.columns(3)
        c4.metric("🏆 이달의 신규 우수 회원", f"{len(vip_df)}명", "+2명")
        c5.metric("🌱 초기 정착 필요 신규회원", "8명", "플랜 수립")
        c6.metric("🎯 정체기 돌파 시급", f"{len(sales_df)}명", "PT 제안 타겟")

    elif menu == "🚨 Epic 1. 이탈 위험 관리":
        st.title("🚨 Epic 1. 이탈 위험 신호 관리")
        st.altair_chart(alt.Chart(churn_df).mark_bar(color='#2563EB').encode(x=alt.X('이탈 확률(%):Q', axis=alt.Axis(title='이탈 확률(%)')), y=alt.Y('회원명:N', sort='-x', axis=alt.Axis(title='회원명')), tooltip=['회원명', '위험 사유', '이탈 확률(%)']).properties(height=300), use_container_width=True)
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        msg_template = st.text_area("맞춤형 복귀 유도 알림톡 템플릿", "회원님, 최근 방문이 뜸하시네요! 이번 주 오시면 혜택을 드립니다.")
        if st.button("일괄 자동 컨택 발송 (Epic 1-2)", type="primary"): st.toast("이탈 위험군 전체 메시지 발송 완료")

    elif menu == "🏆 Epic 2. 우수 회원 관리":
        st.title("🏆 Epic 2. 우수 회원 자동 선별")
        st.dataframe(vip_df, use_container_width=True, hide_index=True)
        if st.button("🎁 선택 회원 재등록 쿠폰/감사 메시지 발송", type="primary"): st.toast("VIP 혜택 발송 완료")

    elif menu == "🎯 Epic 3. PT 영업 및 성장":
        st.title("🎯 Epic 3. 정체기 회원 타겟팅 (PT 영업)")
        st.dataframe(sales_df, column_config={"수행률(%)": st.column_config.ProgressColumn("수행률", min_value=0, max_value=100, format="%d%%")}, hide_index=True, use_container_width=True)
        if st.button("🎟️ 맞춤형 원포인트 PT 쿠폰 일괄 발송", type="primary"): st.toast("영업 쿠폰 발송 완료")

    elif menu == "💬 Epic 4. Q&A 및 소통":
        st.title("💬 Epic 4. 1:1 질문함 실시간 연동")
        for q in st.session_state['qna_db']:
            if q['상태'] == '대기중':
                with st.expander(f"[대기중] {q['유형']} - {q['회원명']}", expanded=True):
                    st.write(f"Q. {q['내용']}")
                    reply = st.text_area("답장 작성", key=f"ans_{q['id']}")
                    if st.button("답장 발송", key=f"btn_{q['id']}", type="primary"):
                        q['상태'] = '답변완료'; q['답변'] = reply; st.rerun()

    # 💡 [업데이트] Epic 5. 기구별 혼잡도 선택 조회 기능 완벽 구현
    elif menu == "🏢 Epic 5. 기구별 혼잡도 분석":
        st.title("🏢 Epic 5. 기구별 맞춤 혼잡도 분석")
        st.write("시간대별 기구 이용률을 확인하고 싶은 종목을 선택하세요.")
        
        # '시간' 컬럼을 제외한 순수 기구 목록 추출
        machine_columns = [col for col in heatmap_df.columns if col != "시간"]
        
        # 1. 다중 선택 (Multi-select) UI 제공 (기본값: 상위 2개 기구)
        selected_machines = st.multiselect(
            "조회할 기구 선택:", 
            options=machine_columns, 
            default=["파워 랙 (웨이트)", "트레드밀 (유산소)"]
        )
        
        if not selected_machines:
            st.warning("조회할 기구를 최소 1개 이상 선택해주세요.")
        else:
            # 2. 선택한 기구만 필터링하여 데이터 변환 (Melt)
            cols_to_keep = ["시간"] + selected_machines
            filtered_df = heatmap_df[cols_to_keep]
            df_melt = filtered_df.melt('시간', var_name='기구', value_name='사용량(%)')
            
            # 3. Area Chart 시각화 적용
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
        st.title("🛠️ Epic 7. 실시간 민원 트래킹")
        for f in st.session_state['facility_db']:
            with st.expander(f"[{f['상태']}] {f['위치']} - {f['신고자']}"):
                st.write(f"민원: {f['내용']}")
                col1, col2 = st.columns([1, 3])
                with col1: status = st.selectbox("상태", ["접수됨", "조치중", "조치완료"], key=f"f_stat_{f['id']}")
                with col2: reply = st.text_input("결과", f['답변'], key=f"f_rep_{f['id']}")
                if st.button("저장", key=f"f_btn_{f['id']}", type="primary"):
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
                if st.button("👟 회원 (B2C) 시연 접속", use_container_width=True):
                    st.session_state['logged_in'] = True; st.session_state['role'] = 'MEMBER'; st.rerun()
            with col_b2:
                if st.button("💼 총괄 점주 (B2B) 시연 접속", use_container_width=True):
                    st.session_state['logged_in'] = True; st.session_state['role'] = 'OWNER'; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        if st.sidebar.button("🚪 시스템 종료 (권한 다시 선택)"):
            st.session_state['logged_in'] = False; st.session_state['role'] = None; st.rerun()
            
        if st.session_state['role'] == 'MEMBER': member_app()
        elif st.session_state['role'] == 'OWNER': owner_app()

if __name__ == "__main__":
    main()
