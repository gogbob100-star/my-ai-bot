import streamlit as st
from google import genai
from gtts import gTTS
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="مساعدي الذكي",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .user-msg {
        background: #e3f2fd;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        text-align: right;
        color: #000;
    }
    .bot-msg {
        background: #f3e5f5;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        text-align: right;
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🤖 مساعدي الذكي</h1><p>مساعدك الشخصي بالعربي</p></div>', unsafe_allow_html=True)

try:
    API_KEY = st.secrets["GEMINI_KEY"]
except:
    API_KEY = ""

client = genai.Client(api_key=API_KEY)

FILE = "memory.json"

if "history" not in st.session_state:
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            st.session_state.history = json.load(f)
    else:
        st.session_state.history = []

with st.sidebar:
    st.header("⚙️ الإعدادات")
    st.write(f"📊 عدد الرسائل: {len(st.session_state.history)}")
    
    if st.button("🗑️ امسح المحادثة", use_container_width=True):
        st.session_state.history = []
        with open(FILE, "w") as f:
            json.dump([], f)
        st.success("✅ انمسحت الذاكرة")
        st.rerun()
    
    if st.button("🔊 تشغيل آخر رد", use_container_width=True):
        if st.session_state.history:
            آخر_رد = st.session_state.history[-1]["البوت"]
            tts = gTTS(text=آخر_رد, lang="ar")
            tts.save("رد.mp3")
            st.audio("رد.mp3", autoplay=True)

st.subheader("💬 المحادثة")

for msg in st.session_state.history:
    st.markdown(f'<div class="user-msg">👤 <b>أنت:</b> {msg["أنت"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot-msg">🤖 <b>البوت:</b> {msg["البوت"]}</div>', unsafe_allow_html=True)

سؤال = st.chat_input("اكتب سؤالك هنا...")

if سؤال:
    st.session_state.history.append({"أنت": سؤال, "البوت": "..."})
    
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"المحادثة السابقة: {st.session_state.history[:-1]}\n\nالسؤال: {سؤال}"
        )
        رد = response.text
        st.session_state.history[-1]["البوت"] = رد
        
        with open(FILE, "w") as f:
            json.dump(st.session_state.history, f, ensure_ascii=False)
        
        st.rerun()
    except Exception as e:
        st.error(f"⚠️ خطأ: {e}")