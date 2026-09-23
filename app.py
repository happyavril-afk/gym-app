import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="스마트 헬스장 B2B2C", page_icon="⚡", layout="wide")

# 2. 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
if 'msg_history' not in st.session_state:
    st.session_state['msg_history'] = []
if 'qna_db' not in st.session_state:
    st.session_state['qna_db'] = [
        {"id": 1, "시간": "오늘 14:20", "회원명": "박수민", "유형": "🏋️ 운동/자세 피드백", "내용": "벤치프레스 할 때 오른쪽 어깨가 결려요. 바벨 위치 문제일까요?", "상태": "대기중", "답변": ""},
        {"id": 2, "시간": "오늘 13:05", "회원명": "김민지", "유형": "💳 회원권/PT 문의", "내용": "PT 10회 추가 결제하면 할인 혜택이 어떻게 되나요?", "상태": "대기중", "답변": ""},
        {"id": 3, "시간": "어제 20:10", "회원명": "장도연", "유형": "🏢 시설 이용 문의", "내용": "여자 탈의실 3번 락커 문이 잘 안 닫힙니다. 확인 부탁드려요.", "상태": "답변완료", "답변": "불편을 드려 죄송합니다! 시설팀에 바로 전달하여 수리 완료했습니다."},
    ]

# ==========================================
# 🎨 다이내믹 커스텀 CSS (아이콘 글자 겹침 완벽 해결)
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
    
    /* 🌟 1. 일반 텍스트 폰트 적용 (아이콘 보호를 위해 포괄적 태그 제외) */
    p, h1, h2, h3, h4, h5, h6, label, li, a, button, b, strong, svg text, canvas {
        font-family: 'GmarketSans', 'Montserrat', sans-serif !important;
        letter-spacing: -0.5px;
    }
    
    /* 🌟 2. 표(DataFrame) 내부 폰트 적용 */
    [data-testid="stDataFrame"] div, [data-testid="stTable"] th, [data-testid="stTable"] td {
        font-family: 'GmarketSans', sans-serif !important;
    }
    
    /* 🚨 3. 스트림릿 아이콘 폰트 강제 복구 (글자 겹침 현상 원천 차단) */
    span.material-symbols-rounded, span.material-icons, .stIcon, [class*="st-icon"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state['logged_in']:
        # 🔥 로그인 폼
        st.markdown("""
        <style>
        .stApp {
            background-image: linear-gradient(rgba(10, 10, 12, 0.65), rgba(10, 10, 12, 0.85)), url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        .hero-title { font-family: 'Montserrat', 'GmarketSans', sans-serif !important; font-size: 5.5rem; font-weight: 900; color: #ffffff; text-transform: uppercase; text-align: center; margin-top: 15vh; margin-bottom: 0px; text-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .hero-subtitle { font-size: 1.6rem; color: #ccff00; text-align: center; font-weight: 700; margin-bottom: 60px; text-shadow: 0 2px 10px rgba(204,255,0,0.3); }
        .login-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 40px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); }
        .stButton>button { border-radius: 30px !important; font-size: 1.6rem !important; font-weight: 900 !important; padding: 2.2rem 0 !important; background: transparent !important; border: 2px solid #ccff00 !important; color: #ccff00 !important; transition: all 0.3s ease !important; }
        .stButton>button:hover { background: #ccff00 !important; color: #111 !important; box-shadow: 0 0 20px rgba(204,255,0,0.5) !important; transform: scale(1.03); }
        </style>
        """, unsafe_allow_html=True)

    elif st.session_state['role'] == 'MEMBER':
        # 👟 회원 화면
        st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; background-image: radial-gradient(at 0% 0%, #1e1b4b 0, transparent 50%), radial-gradient(at 100% 0%, #312e81 0, transparent 50%) !important; background-attachment: fixed !important; }
        
        /* 회원 사이드 텍스트 컬러 화이트 강제 (아이콘 클래스 제외) */
        .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
        .stApp span:not([class*="stIcon"]):not(.material-icons), .stApp label, .stApp b, .stApp li, .stApp div[data-testid="stMarkdownContainer"] { color: #ffffff !important; }
        
        .insta-gradient-text { font-family: 'Montserrat', sans-serif !important; background: linear-gradient(to right, #00f2fe, #4facfe) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-weight: 900 !important; font-size: 2.8rem !important; margin-bottom: 15px !important; text-align: center !important; text-transform: uppercase !important; }
        .profile-card { background: rgba(255, 255, 255, 0.12) !important; backdrop-filter: blur(16px) !important; -webkit-backdrop-filter: blur(16px) !important; border-radius: 24px !important; padding: 25px !important; border: 1px solid rgba(255, 255, 255, 0.25) !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important; margin-bottom: 25px !important; }
        div[data-testid="stAlert"] { background-color: rgba(255, 255, 255, 0.1) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; }
        .stButton>button { border-radius: 30px !important; font-weight: 800 !important; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important; color: #111 !important; border: none !important; font-size: 1.2rem !important; padding: 1.5rem !important; }
        .stSelectbox div[data-baseweb="select"] > div, .stNumberInput div[data-baseweb="input"] > div, .stTextArea textarea { background-color: rgba(0,0,0,0.4) !important; color: white !important; border: 1px solid rgba(255,255,255,0.3) !important; }
        </style>
        """, unsafe_allow_html=True)
        
    elif st.session_state['role'] == 'OWNER':
        # 💼 점주 화면
        st.markdown("""
        <style>
        .stApp { background-color: #F4F7F9; }
        .corp-card { background-color: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); border-left: 6px solid #2563EB; margin-bottom: 25px; }
        h1, h2, h3 { color: #1e293b; font-weight: 900; }
        .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
        .stButton>button { border-radius: 8px !important; font-weight: 700 !important; background-color: #2563EB !important; color: #fff !important; font-size: 1.05rem !important; padding: 0.6rem !important; border: none !important; }
        .stButton>button:hover { background-color: #1D4ED8 !important; }
        div[data-testid="metric-container"] { background-color: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); border: 1px solid #e2e8f0; }
        .reply-box { background-color: #f1f5f9; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981; margin-top: 10px; }
        </style>
        """, unsafe_allow_html=True)

# ==========================================
# 📱 회원 (MEMBER) 앱 화면 (사이드바 메뉴로 개편)
# ==========================================
def member_app():
    st.sidebar.markdown(f"**👟 회원 (B2C) 내비게이션**")
    menu = st.sidebar.radio("📋 메뉴 선택", [
        "🚀 오늘의 처방", 
        "📡 기구 스캔 (NFC)", 
        "📈 과거 운동 이력", 
        "📸 오운완 스토리",
        "💬 1:1 질문함"
    ])

    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<div class='insta-gradient-text'>Today's Fit</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='profile-card'>
            <span style='font-size: 1.2rem;'><b>@soomin_workout</b>님, 오늘 하루도 득근하세요! 🔥</span><br><br>
            <span style='color: #ccff00 !important; font-size: 1.1rem; font-weight: bold;'>보유 포인트: 1,550 P</span>
        </div>
        """, unsafe_allow_html=True)
        
        if menu == "🚀 오늘의 처방":
            st.markdown("<h3 style='padding-top: 10px;'>🤖 AI 맞춤 운동 처방</h3>", unsafe_allow_html=True)
            st.info("💡 최근 2주간 하체 볼륨이 상체에 비해 40% 부족합니다. 오늘은 하체(대퇴사두) 중심 루틴을 제안합니다.")
            
            st.checkbox("워밍업: 스텝밀(천국의 계단) 10분")
            st.checkbox("메인 1: 파워 랙(스쿼트) 80kg x 10회 (4세트)")
            st.checkbox("메인 2: 레그 프레스 120kg x 12회 (3세트)")
            st.checkbox("마무리: 레그 익스텐션 40kg x 15회 (3세트)")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💪 운동 시작하기 (워치 연동)", use_container_width=True):
                st.toast("운동이 시작되었습니다! 부상에 주의하세요.")

        elif menu == "📡 기구 스캔 (NFC)":
            st.markdown("<h3 style='padding-top: 10px;'>📡 NFC 기구 스캔 (원터치 갱신)</h3>", unsafe_allow_html=True)
            machine_list = [
                "기구를 선택하세요 (태그 대기 중...)",
                "--- [ 프리웨이트 & 랙 ] ---", "파워 랙 (스쿼트/데드리프트)", "스미스 머신 (전신)", 
                "--- [ 상체 머신 ] ---", "벤치프레스 머신 (가슴)", "랫풀다운 (등)", 
                "--- [ 하체 머신 ] ---", "레그 프레스 (하체)", "레그 익스텐션 (앞허벅지)", 
                "--- [ 유산소 ] ---", "트레드밀 (러닝머신)"
            ]
            machine = st.selectbox("가상 NFC 태그 시뮬레이터:", machine_list)
            
            if machine != "기구를 선택하세요 (태그 대기 중...)" and not machine.startswith("---"):
                st.success(f"✅ {machine} 인식 완료")
                if "유산소" in machine or "트레드밀" in machine:
                    st.info("🏃 유산소 운동은 심박수와 소모 칼로리가 자동 기록됩니다.")
                    if st.button("유산소 세션 시작", use_container_width=True):
                        st.toast("유산소 기록이 시작되었습니다.")
                else:
                    st.info(f"💡 최근 수행하신 {machine} 기록을 불러왔습니다.")
                    col_w, col_r = st.columns(2)
                    with col_w:
                        weight = st.number_input("중량 (kg)", value=50, step=5)
                    with col_r:
                        reps = st.number_input("반복 횟수", value=12, step=1)
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💪 이 기록으로 원터치 세트 완료", use_container_width=True):
                        st.toast(f"{machine} 기록 완료! 🔥 휴식 타이머 시작.")
            
        elif menu == "📈 과거 운동 이력":
            st.markdown("<h3 style='padding-top: 10px;'>📈 과거 운동 이력</h3>", unsafe_allow_html=True)
            history_data = pd.DataFrame({
                "날짜": ["09.05", "09.08", "09.12", "09.15", "09.18", "09.21"],
                "운동 부위": ["가슴", "하체", "등", "어깨/팔", "가슴", "하체"],
                "주요 기구": ["벤치프레스", "파워 랙", "랫풀다운", "숄더 프레스", "벤치프레스", "레그 프레스"],
                "총 볼륨(kg)": [2400, 4200, 2100, 1500, 2800, 4800]
            })
            
            chart_history = alt.Chart(history_data).mark_line(point=True, color='#00f2fe').encode(
                x=alt.X('날짜:O', sort=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y('총 볼륨(kg):Q', scale=alt.Scale(zero=False)),
                tooltip=['날짜', '총 볼륨(kg)']
            ).properties(height=250)
            st.altair_chart(chart_history, use_container_width=True)
            st.dataframe(history_data, hide_index=True, use_container_width=True)

        elif menu == "📸 오운완 스토리":
            st.markdown("<h3 style='padding-top: 10px;'>📸 나의 오운완 스토리</h3>", unsafe_allow_html=True)
            st.image("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop", caption="#오운완")
            st.write("소모 칼로리: **450 kcal** | 누적 볼륨: **3,200 kg**")
            st.button("인스타그램 공유", use_container_width=True)
            
        elif menu == "💬 1:1 질문함":
            st.markdown("<h3 style='padding-top: 10px;'>💬 1:1 질문함</h3>", unsafe_allow_html=True)
            st.write("궁금한 점을 남겨주시면 관리자가 실시간으로 답변해 드립니다.")
            
            q_category = st.selectbox("문의 유형 선택", [
                "🏋️ 운동/자세 피드백", 
                "🏢 시설 이용 문의", 
                "💳 회원권/PT 영업 문의", 
                "⚙️ 앱/시스템 오류", 
                "💡 기타"
            ])
            q_text = st.text_area("질문 내용", placeholder="자세한 내용을 입력해주세요.")
            
            if st.button("질문 전송하기", use_container_width=True):
                if q_text:
                    new_q = {
                        "id": len(st.session_state['qna_db']) + 1,
                        "시간": "방금 전",
                        "회원명": "박수민(본인)",
                        "유형": q_category,
                        "내용": q_text,
                        "상태": "대기중",
                        "답변": ""
                    }
                    st.session_state['qna_db'].insert(0, new_q)
                    st.toast("질문이 성공적으로 접수되었습니다!")
                    st.rerun()
                else:
                    st.error("질문 내용을 입력해주세요.")
            
            st.markdown("---")
            st.markdown("#### 나의 문의 내역")
            for q in st.session_state['qna_db']:
                if q['회원명'] in ["박수민", "박수민(본인)"]:
                    with st.expander(f"[{q['상태']}] {q['유형']} - {q['시간']}"):
                        st.write(f"**Q. {q['내용']}**")
                        if q['상태'] == "답변완료":
                            st.info(f"**A. 관리자 답변:**\n{q['답변']}")
                        else:
                            st.warning("답변을 준비 중입니다.")

# ==========================================
# 💻 점주 (OWNER) B2B 대시보드
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
        
        col1, col2, col3 = st.columns(3)
        col1.metric("이번 주 신규 이탈 위험군", "12명", "+3명 🔺")
        col2.metric("AI 예측 이탈 방어 성공률", "68.5%", "4.2% 🔺")
        col3.metric("위험군 전체 복귀 시 예상 매출", "4,200,000원", "-")
        
        reason_data = pd.DataFrame({"요인": ["장기 미방문 (14일+)", "방문 빈도 급감", "계약 만료 임박"], "회원 수": [45, 28, 12]})
        chart = alt.Chart(reason_data).mark_bar(color='#2563EB').encode(
            x=alt.X('요인:O', sort=None, axis=alt.Axis(labelAngle=0, title='위험 사유 분류')),
            y=alt.Y('회원 수:Q', axis=alt.Axis(title='회원 수(명)')),
            tooltip=['요인', '회원 수']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        
        churn_df = pd.DataFrame({
            "회원명": ["김철수", "박지민", "이동국", "한소희", "마동석"],
            "위험 사유": ["조건 A (18일 미방문)", "조건 B (주 4회➔1회)", "조건 A (24일 미방문)", "조건 B (주 5회➔2회)", "만료 D-5 & 미방문"],
            "이탈 확률(AI)": ["88%", "75%", "96%", "68%", "92%"],
            "회원권 잔여일": ["45일", "120일", "12일", "200일", "5일"]
        })
        st.dataframe(churn_df, use_container_width=True, hide_index=True)
        
        st.markdown("<h3>✉️ 1-2. 맞춤형 복귀 유도 알림톡 발송</h3>", unsafe_allow_html=True)
        msg_template = st.text_area("발송할 메시지 내용 수정", "회원님, 최근 헬스장 방문이 뜸하시네요! 🏃‍♂️\n이번 주에 방문하시면 7일 기간 연장 혜택을 드립니다.")
        if st.button("위험군 전체에게 알림톡 전송", type="primary"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state['msg_history'].insert(0, {"발송 시간": now, "대상": "이탈 위험군 전체", "발송 내용": msg_template, "유형": "복귀 유도"})
            st.success("메시지가 성공적으로 발송되었습니다.")
            
        if st.session_state['msg_history']:
            with st.expander("📝 최근 발송 이력 보기", expanded=False):
                st.dataframe(pd.DataFrame(st.session_state['msg_history']), hide_index=True, use_container_width=True)

    elif menu == "🎯 Epic 2. PT 타겟팅 & 영업":
        st.title("🎯 정체기 회원 타겟팅 (PT 영업 보드)")
        
        sales_df = pd.DataFrame({
            "회원명": ["최운식", "정종현", "이광수", "전소민", "하동훈"],
            "정체 종목": ["벤치프레스", "스쿼트", "데드리프트", "숄더 프레스", "레그 프레스"],
            "정체 기간": ["4주째 50kg", "3주째 80kg", "5주째 60kg", "8주째 15kg", "3주째 100kg"],
            "AI 추천 세일즈 액션": ["자세 교정 제안", "보조 운동 제안", "하체 루틴 변경", "유연성 집중 레슨", "고중량 안전 보조"],
            "수행률": [65, 40, 80, 25, 30] 
        })
        st.dataframe(sales_df, column_config={"수행률": st.column_config.ProgressColumn("운동계획 수행률", min_value=0, max_value=100, format="%d%%")}, hide_index=True, use_container_width=True)
        
        st.markdown("<h3>📈 개별 회원 정체기 시계열 분석</h3>", unsafe_allow_html=True)
        selected_member = st.selectbox("변화 추이를 분석할 회원을 선택하세요:", sales_df['회원명'])
        
        target_exercise = sales_df.loc[sales_df['회원명'] == selected_member, '정체 종목'].values[0]
        plateau_data = pd.DataFrame({"주차": ["6주 전", "5주 전", "4주 전", "3주 전", "2주 전", "이번 주"], "중량(kg)": [40, 45, 50, 50, 50, 50]})
        
        chart2 = alt.Chart(plateau_data).mark_line(point=True, color='#2563EB').encode(
            x=alt.X('주차:O', sort=None, axis=alt.Axis(labelAngle=0, title='주차')),
            y=alt.Y('중량(kg):Q', scale=alt.Scale(zero=False)),
            tooltip=['주차', '중량(kg)']
        ).properties(height=250)
        st.altair_chart(chart2, use_container_width=True)

        st.markdown("<h3>🎟️ 원포인트 PT 쿠폰 맞춤 발송</h3>", unsafe_allow_html=True)
        target_members = st.multiselect("쿠폰 발송 대상을 선택하세요", sales_df['회원명'].tolist(), default=sales_df['회원명'].tolist())
        pt_msg = st.text_area("쿠폰 발송 메시지 수정", "회원님, '무료 1:1 원포인트 레슨 쿠폰'을 보내드리니 데스크로 편하게 문의주세요!")
        
        if st.button("💪 선택한 회원에게 쿠폰 발송하기", type="primary"):
            if len(target_members) > 0:
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state['msg_history'].insert(0, {"발송 시간": now, "대상": f"정체기 회원 {len(target_members)}명", "발송 내용": pt_msg, "유형": "PT 영업 쿠폰"})
                st.success(f"{len(target_members)}명의 회원에게 영업 제안이 전송되었습니다.")
                
        if st.session_state['msg_history']:
            with st.expander("📝 최근 발송 이력 보기", expanded=False):
                st.dataframe(pd.DataFrame(st.session_state['msg_history']), hide_index=True, use_container_width=True)

    elif menu == "💬 Epic 3. AI 소통 & 회원 CS":
        st.title("💬 실시간 회원 Q&A 및 소통 대시보드")
        
        pending_count = sum(1 for q in st.session_state['qna_db'] if q['상태'] == '대기중')
        col1, col2, col3 = st.columns(3)
        col1.metric("이번 달 AI 자동 발송", "156건", "42건 🔺")
        col2.metric("미해결 CS 질문", f"{pending_count}건", "실시간 연동중")
        col3.metric("CS 평균 응답 시간", "25분", "-5분 🔻")
        
        st.markdown("<div class='corp-card'><b>🙋‍♂️ 접수된 회원 질문함 (실시간)</b><br>유형별로 접수된 문의를 확인하고 즉시 답장을 발송할 수 있습니다.</div>", unsafe_allow_html=True)
        
        q_tab1, q_tab2 = st.tabs([f"🚨 대기중인 질문 ({pending_count})", "✅ 답변 완료 내역"])
        
        with q_tab1:
            if pending_count == 0:
                st.info("모든 질문에 대한 답변이 완료되었습니다.")
            
            for q in st.session_state['qna_db']:
                if q['상태'] == '대기중':
                    with st.expander(f"[{q['유형']}] {q['회원명']} 회원님 - {q['시간']}", expanded=True):
                        st.markdown(f"**Q. {q['내용']}**")
                        reply_text = st.text_area("답장 작성", key=f"reply_{q['id']}", placeholder="회원님께 전달할 답변을 작성해주세요.")
                        
                        if st.button("답장 발송", key=f"btn_{q['id']}", type="primary"):
                            if reply_text:
                                for db_q in st.session_state['qna_db']:
                                    if db_q['id'] == q['id']:
                                        db_q['상태'] = '답변완료'
                                        db_q['답변'] = reply_text
                                st.toast(f"{q['회원명']} 회원님께 답변이 발송되었습니다!")
                                st.rerun()
                            else:
                                st.error("답변 내용을 입력해주세요.")
                                
        with q_tab2:
            for q in st.session_state['qna_db']:
                if q['상태'] == '답변완료':
                    with st.expander(f"[{q['유형']}] {q['회원명']} 회원님 - {q['시간']}"):
                        st.markdown(f"**Q. {q['내용']}**")
                        st.markdown(f"<div class='reply-box'><b>A. 관리자 답변:</b><br>{q['답변']}</div>", unsafe_allow_html=True)

    elif menu == "🏢 Epic 4. 시설 혼잡도 분석":
        st.title("🏢 기구 혼잡도(히트맵) 및 공간 최적화")
        
        heatmap_data = pd.DataFrame({
            "시간대": ["09:00", "11:00", "13:00", "15:00", "17:00", "18:00", "19:00", "20:00", "22:00"],
            "파워 랙 (스쿼트)": [15, 30, 45, 55, 80, 100, 95, 85, 60],
            "트레드밀 (유산소)": [40, 50, 70, 65, 95, 90, 80, 75, 60],
            "랫풀다운": [20, 35, 45, 50, 75, 85, 70, 65, 45]
        })
        df_melted = heatmap_data.melt('시간대', var_name='기구', value_name='누적 사용량')
        
        area_chart = alt.Chart(df_melted).mark_area(opacity=0.6).encode(
            x=alt.X('시간대:O', sort=None, axis=alt.Axis(labelAngle=0, title='시간대')),
            y=alt.Y('누적 사용량:Q', stack=None, axis=alt.Axis(title='누적 사용량')),
            color=alt.Color('기구:N', legend=alt.Legend(orient='bottom', title=None)),
            tooltip=['시간대', '기구', '누적 사용량']
        ).properties(height=350)
        st.altair_chart(area_chart, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📉 낮 시간대(13시~16시) 방문 이력 회원군 '오프피크 전용 혜택' 발송", use_container_width=True):
            st.toast("오프피크 방문 유도 쿠폰이 성공적으로 발송되었습니다.")

    elif menu == "🔒 Epic 5. 개인정보 동의 현황":
        st.title("🔒 Privacy Compliance 및 동의 관리")
        
        privacy_df = pd.DataFrame({
            "회원명": ["김철수", "박지민 (철회)", "이지은", "마동석", "한소희 (만료)"],
            "코칭 데이터 활용 동의": ["동의함 🟢", "동의 철회 🚫", "동의함 🟢", "동의함 🟢", "기간 만료 🚫"],
            "체중 / 체성분 데이터 열람": [
                "75.2kg / 골격근 35.1kg", 
                "*** / *** (블라인드 처리)", 
                "52.4kg / 체지방 21%", 
                "105kg / 골격근 50kg", 
                "*** / *** (자동 파기)"
            ],
            "데이터 보유 기한": ["2028-12-31", "파기 대기", "2029-05-15", "2027-10-20", "2026-09-01"]
        })
        st.dataframe(privacy_df, hide_index=True, use_container_width=True)

# ==========================================
# 🚀 메인 라우팅 (컨트롤 타워)
# ==========================================
def main():
    inject_custom_css()
    
    if not st.session_state['logged_in']:
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
