import streamlit as st
import base64
from PIL import Image
import json
import time
from backend import GenerateResponse
from fpdf import FPDF
from io import StringIO
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import datetime
import re

# --- GLOBAL NAVIGATION & TOGGLE GUARD ---
# This ensures that browser backward/forward arrows do not cause a blank screen
if "page" not in st.session_state:
    st.session_state.page = "home"

# Page config must be outside of any conditional blocks to maintain state during navigation
st.set_page_config(page_title="AETHER AI", page_icon="💠", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# CODE 1: THE UI DESIGN (HOME PAGE)
# ---------------------------------------------------------
if st.session_state.page == "home":
    def inject_pro_css():
        st.markdown("""
            <style>
                /* Hide Streamlit elements for a clean 'App' look */
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                
                /* Main Background */
                .stApp {
                    background: #050505;
                    color: #ffffff;
                    font-family: 'Inter', sans-serif;
                }

                /* The Floating AI Orb Animation */
                .orb-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 300px;
                }
                .orb {
                    width: 150px;
                    height: 150px;
                    background: radial-gradient(circle at 30% 30%, #00f2fe, #4facfe);
                    border-radius: 50%;
                    box-shadow: 0 0 50px #00f2fe, 0 0 100px #4facfe, inset 0 0 50px rgba(255,255,255,0.2);
                    animation: float 4s ease-in-out infinite, pulse 2s infinite alternate;
                }
                @keyframes float {
                    0% { transform: translateY(0px) rotate(0deg); }
                    50% { transform: translateY(-20px) rotate(10deg); }
                    100% { transform: translateY(0px) rotate(0deg); }
                }
                @keyframes pulse {
                    0% { box-shadow: 0 0 30px #00f2fe; }
                    100% { box-shadow: 0 0 70px #4facfe; }
                }

                /* Modern Hero Text */
                .hero-text {
                    text-align: center;
                    font-weight: 900;
                    letter-spacing: -3px;
                    font-size: 6rem;
                    background: linear-gradient(to bottom, #ffffff 30%, #444 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-top: -20px;
                }

                /* Satisfying Glass Cards */
                .glass-card {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 24px;
                    padding: 30px;
                    transition: 0.4s all;
                    text-align: center;
                }
                .glass-card:hover {
                    background: rgba(255, 255, 255, 0.07);
                    border: 1px solid #00f2fe;
                    transform: translateY(-10px);
                }
            </style>
        """, unsafe_allow_html=True)

    inject_pro_css()

    st.markdown('<div class="orb-container"><div class="orb"></div></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-text">AETHER</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#666; font-size:1.5rem; margin-top:-20px;">The Next Dimension of Intelligence</p>', unsafe_allow_html=True)
    st.write("##")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown('<div class="glass-card"><h3>Vision</h3><p>Real-time image perception and neural analysis.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><h3>Logic</h3><p>Advanced reasoning and code generation capabilities.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card"><h3>Global</h3><p>Instant translation across 100+ languages.</p></div>', unsafe_allow_html=True)

    st.write("##")
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        if st.button("INITIALIZE CORE", use_container_width=True):
            with st.spinner("Calibrating Neural Pathways..."):
                time.sleep(1.5)
                st.session_state.page = "appsample"
                st.rerun()

# ---------------------------------------------------------
# CODE 2: APPSAMPLE.PY (CHATBOT LOGIC)
# ---------------------------------------------------------
elif st.session_state.page == "appsample":
    def load_users():
        try:
            with open('users.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_users(user_db):
        with open('users.json', 'w') as file:
            json.dump(user_db, file)

    def download_text(messages):
        chat_content = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
        text_file = StringIO()
        text_file.write(chat_content)
        text_file.seek(0)
        return text_file.getvalue().encode('utf-8')

    def download_pdf(messages):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for m in messages:
            sanitized_content = m['content'].encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 10, f"{m['role'].capitalize()}: {sanitized_content}")
        return pdf.output(dest='S').encode('latin1')

    def detect_language(text):
        try:
            return detect(text)
        except LangDetectException:
            return 'en'

    def translate_text(text, target_lang='en'):
        try:
            return GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception:
            return text

    def response_generator(messages, image=None):
        last_user_msg = next((m for m in reversed(messages) if m["role"] == "user"), None)
        if not last_user_msg:
            return GenerateResponse("", image)

        user_text = last_user_msg["content"].lower()

        if "tomorrow" in user_text and "date" in user_text:
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            return f"Tomorrow's date is {tomorrow.strftime('%d-%m-%Y')}."

        explain_match = re.search(r'explain.*in\s+(\w+)', user_text)
        if explain_match:
            target_lang = explain_match.group(1).lower()
            last_code = None
            for msg in reversed(messages):
                if msg["role"] == "assistant" and "```" in msg["content"]:
                    last_code = msg["content"]
                    break
            if last_code:
                prompt = (
                    f"Convert the following code to {target_lang} and explain it:\n"
                    f"{last_code}\n"
                    f"Please provide the code in {target_lang} with explanation."
                )
                return GenerateResponse(prompt, image)

        prompt_lines = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if content:
                prompt_lines.append(f"{role.capitalize()}: {content}")
        
        full_prompt = "\n".join(prompt_lines)
        return GenerateResponse(full_prompt, image)

    st.markdown("""
        <style>
            .stTextInput>div>div>input {
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ccc;
            }
            .stButton>button {
                background-color: #2ecc71;
                color: white;
                border-radius: 30px;
                padding: 8px 20px;
                font-weight: bold;
            }
            .stButton>button:hover {
                background-color: #27ae60;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "sub_page" not in st.session_state:
        st.session_state.sub_page = "login"

    user_db = load_users()

    if st.session_state.sub_page == "login":
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("## Login to Your Account")
            username = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", placeholder="Enter your password", type="password")

            if st.button("Login", use_container_width=True):
                stored_password = user_db.get(username)
                if stored_password and password == stored_password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.sub_page = "chatbot"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with col2:
            st.markdown("## New Here?")
            if st.button("Sign Up", use_container_width=True):
                st.session_state.sub_page = "signup"
                st.rerun()

    elif st.session_state.sub_page == "signup":
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("## ✍ Signup for Chatbot")
            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password", type="password")

            if st.button("Create Account", use_container_width=True):
                if new_username in user_db:
                    st.error("Username already exists.")
                else:
                    user_db[new_username] = new_password
                    save_users(user_db)
                    st.session_state.sub_page = "login"
                    st.rerun()

        with col2:
            if st.button("Go to Login", use_container_width=True):
                st.session_state.sub_page = "login"
                st.rerun()

    elif st.session_state.sub_page == "chatbot" and st.session_state.authenticated:
        st.title("🧠 Chatbot")

        st.sidebar.title("Chat Options")
        if st.session_state.messages:
            st.sidebar.download_button("📄 Download Chat (Text)", download_text(st.session_state.messages), file_name="chat_history.txt")
            st.sidebar.download_button("📄 Download Chat (PDF)", download_pdf(st.session_state.messages), file_name="chat_history.pdf")
        
        if st.sidebar.button("🧹 Clear Chat & History"):
            st.session_state.messages.clear()
            st.session_state.uploader_key += 1
            st.session_state.uploaded_image = None
            st.rerun()

        if st.sidebar.button("🔒 Logout"):
            st.session_state.authenticated = False
            st.session_state.sub_page = "login"
            st.rerun()

        uploaded_file = st.sidebar.file_uploader("Upload Image:", type=["jpg", "png"], key=f"img_{st.session_state.uploader_key}")
        if uploaded_file:
            st.session_state.uploaded_image = Image.open(uploaded_file)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if 'image' in msg:
                    st.image(msg['image'], use_container_width=True)

        if prompt := st.chat_input("Type your message..."):
            user_msg = {"role": "user", "content": prompt}
            if st.session_state.uploaded_image:
                user_msg['image'] = st.session_state.uploaded_image
            st.session_state.messages.append(user_msg)

            response = response_generator(st.session_state.messages, st.session_state.uploaded_image)
            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.uploaded_image = None
            st.rerun()