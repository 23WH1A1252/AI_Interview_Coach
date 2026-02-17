import streamlit as st
import pandas as pd
import os
import sqlite3
from streamlit_webrtc import webrtc_streamer
from live_camera import FaceDetector
from datetime import datetime

from database import create_tables
from speech_to_text import convert_speech_to_text
from auth import register_user, login_user

# ================= STREAMLIT CONFIG =================
st.set_page_config(
    page_title="AI Driven Interview Coach",
    page_icon="🎤",
    layout="centered"
)

# ================= 🎨 PREMIUM UI =================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Glass Card */
.card {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(14px);
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    margin-bottom: 20px;
    color: white;
}

/* Title */
.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    color: white;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 3em;
    font-weight: 600;
    border: none;
    background: linear-gradient(135deg,#ff7a18,#ffb347);
    color: white;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 10px;
    backdrop-filter: blur(10px);
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================
create_tables()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = None

if "questions" not in st.session_state:
    st.session_state.questions = [
        "Tell me about yourself",
        "What are your strengths?",
        "What are your weaknesses?",
        "Why should we hire you?",
        "Where do you see yourself in 5 years?"
    ]

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "audio_path" not in st.session_state:
    st.session_state.audio_path = None

if "confidence" not in st.session_state:
    st.session_state.confidence = None

if "all_performance" not in st.session_state:
    st.session_state.all_performance = []

# ================= HEADER =================
st.markdown('<div class="main-title">🎤 AI Interview Coach</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# =================================================
# 🔐 LOGIN PAGE
# =================================================
if st.session_state.page == "login":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔐 Login")

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Login"):
            user = login_user(username, password)
            if user:
                st.session_state.user = username
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password")

    with col2:
        if st.button("📝 Register"):
            st.session_state.page = "register"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =================================================
# 📝 REGISTER PAGE
# =================================================
elif st.session_state.page == "register":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Register")

    username = st.text_input("Choose Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        if register_user(username, email, password):
            st.success("Registration successful! Please login.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Username already exists")

    if st.button("⬅ Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =================================================
# 🏠 DASHBOARD
# =================================================
elif st.session_state.page == "dashboard":

    st.markdown(f"""
    <div class="card">
        <h2>👋 Welcome, {st.session_state.user}</h2>
        <p>Practice interviews and improve your confidence.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎤 Start Interview"):
            st.session_state.current_question = 0
            st.session_state.page = "interview"
            st.rerun()

    with col2:
        if st.button("📈 View Progress"):
            st.session_state.page = "progress"
            st.rerun()

    with col3:
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

# =================================================
# 🎤 INTERVIEW PAGE
# =================================================
elif st.session_state.page == "interview":

    st.subheader("🎤 Interview Practice")

    # ✅ SAFE PROGRESS
    total_q = len(st.session_state.questions)
    current_q = st.session_state.current_question

    progress = current_q / total_q if total_q > 0 else 0
    progress = max(0.0, min(progress, 1.0))

    st.progress(progress)
    st.caption(f"Progress: {progress*100:.0f}%")

    # ✅ QUESTION COMPLETE CHECK
    if current_q >= total_q:
        st.success("🎉 Interview completed!")
        st.session_state.page = "progress"
        st.rerun()

    question = st.session_state.questions[current_q]
    st.info(f"**Question:** {question}")

    # ---------------- AUDIO ----------------
    audio_file = st.audio_input("🎙️ Record your answer")

    if audio_file:
        os.makedirs("recordings", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"recordings/{st.session_state.user}_{timestamp}.wav"

        with open(path, "wb") as f:
            f.write(audio_file.read())

        st.session_state.audio_path = path
        st.success("✅ Audio recorded")

    # ---------------- CAMERA ----------------
    st.divider()
    st.subheader("📷 Live Confidence Monitoring")

    ctx = webrtc_streamer(
        key="camera",
        video_transformer_factory=FaceDetector,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    # ---------------- ANALYZE ----------------
    if st.button("💾 Analyze & Save"):

        if not st.session_state.audio_path:
            st.error("⚠️ Please record audio first")
            st.stop()

        transcript = convert_speech_to_text(st.session_state.audio_path)

        if not transcript or transcript.strip() == "":
            st.error("⚠️ Speech not detected properly")
            st.stop()

        st.markdown("### 📝 Transcript")
        st.success(transcript)

        filler_count = (
            transcript.lower().count("um")
            + transcript.lower().count("uh")
            + transcript.lower().count("like")
        )

        word_count = len(transcript.split())

        # ✅ REALISTIC SCORE
        score = max(30, min(100, 100 - filler_count * 4 + min(word_count * 0.4, 10)))

        # save DB
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interviews (username, transcript, audio_path, confidence) VALUES (?, ?, ?, ?)",
            (st.session_state.user, transcript, st.session_state.audio_path, score),
        )
        conn.commit()
        conn.close()

        # save session
        st.session_state.all_performance.append({
            "Confidence": score,
            "Fillers": filler_count,
            "Words": word_count
        })

        st.success(f"✅ Saved! Confidence Score: {score}%")

    # ---------------- NEXT ----------------
    if st.button("➡ Next Question"):
        st.session_state.current_question += 1
        st.session_state.audio_path = None
        st.rerun()

# =================================================
# 📈 PROGRESS PAGE
# =================================================
elif st.session_state.page == "progress":

    st.subheader("📈 Performance Analytics")

    if st.session_state.all_performance:
        df = pd.DataFrame(st.session_state.all_performance)

        col1, col2 = st.columns(2)
        col1.metric("Average Confidence", f"{int(df['Confidence'].mean())}%")
        col2.metric("Total Fillers", int(df["Fillers"].sum()))

        st.write("### 🎯 Confidence Trend")
        st.line_chart(df["Confidence"])

        st.write("### 🗣️ Filler Words")
        st.bar_chart(df["Fillers"])

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No performance data yet. Complete an interview first.")

    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
