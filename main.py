import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psutil
import socket
from datetime import datetime
import time
import threading

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="🛡️ AI IDPS - Complete Security Dashboard", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= BACKGROUND IMAGE (ONLY CHANGE) =================
st.markdown("""
<style>
/* ===== BACKGROUND IMAGE ONLY ===== */
.stApp {
    background:
        linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.65)),
        url("background.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

/* Keep text readable */
html, body, [class*="css"] {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ================= YOUR ORIGINAL CSS (UNCHANGED) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    .main-header {font-family: 'Poppins', sans-serif; font-size: 4rem; font-weight: 800; 
                  color: #e5e7eb; text-align: center; margin-bottom: 2rem;}
    .about-title {font-family: 'Poppins', sans-serif; font-size: 3.5rem; font-weight: 900; 
                  text-align: center; margin: 2rem 0;}
    .metric-card {padding: 2rem; border-radius: 20px; color: white; text-align: center;}
    .live-indicator {padding: 1.5rem; border-radius: 20px; font-weight: 700; 
                     font-size: 1.4rem; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ================= BUILT-IN DATASET =================
@st.cache_data
def load_builtin_dataset():
    np.random.seed(42)
    n_normal = 800
    n_anomalies = 200

    normal_ips = ['192.168.1.10','192.168.1.20','10.0.0.5','10.0.0.15']
    anomaly_ips = ['45.79.123.45','198.51.100.78','203.0.113.200']

    data = []
    for _ in range(n_normal):
        data.append([
            np.random.choice(normal_ips),
            np.random.choice([80,443,22]),
            np.random.randint(64,1500),
            np.random.randint(1,20),
            np.random.uniform(500,2000),
            np.random.uniform(1,5),
            np.random.uniform(0,0.3)
        ])

    for _ in range(n_anomalies):
        data.append([
            np.random.choice(anomaly_ips),
            np.random.choice([21,23,445,3389]),
            np.random.randint(5000,65000),
            np.random.randint(100,300),
            np.random.uniform(10000,50000),
            np.random.uniform(0.1,1),
            np.random.uniform(0.75,0.98)
        ])

    df = pd.DataFrame(data, columns=[
        "Source_IP","Port","Packet_Length","Packets",
        "Bytes_Sent","Duration","Threat_Score"
    ])

    df["Timestamp"] = pd.date_range(start="2025-01-01", periods=len(df), freq="10S")
    df["Threat_Level"] = df["Threat_Score"].apply(
        lambda x: "🚨 CRITICAL" if x > 0.85 else "⚠️ HIGH" if x > 0.7 else "✅ NORMAL"
    )
    df["Status"] = df["Threat_Level"].apply(
        lambda x: "🚨 THREAT" if "CRITICAL" in x or "HIGH" in x else "✅ NORMAL"
    )
    df["Action_Taken"] = df["Status"].apply(
        lambda x: "🔒 BLOCKED" if x == "🚨 THREAT" else "✅ ALLOWED"
    )

    return df.sample(frac=1).reset_index(drop=True)

# ================= SESSION STATE =================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "about"
if "file_data" not in st.session_state:
    st.session_state.file_data = None
if "builtin_dataset" not in st.session_state:
    st.session_state.builtin_dataset = load_builtin_dataset()

# ================= HELPER =================
def get_laptop_ips():
    ips = []
    try:
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    ips.append(addr.address)
    except:
        ips = ["192.168.1.X"]
    return ips

# ================= PAGES =================
def about_page():
    st.markdown('<h1 class="about-title">AI-DRIVEN INTRUSION DETECTION & PREVENTION SYSTEM</h1>', unsafe_allow_html=True)
    st.markdown("### 🛡️ Real-Time Cyber Security Command Dashboard")
    if st.button("🔐 START"):
        st.session_state.current_page = "login"
        st.rerun()

def login_page():
    st.markdown('<h1 class="main-header">🔐 Login</h1>', unsafe_allow_html=True)
    with st.form("login"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
    if submit:
        if user == "admin" and pwd == "admin123":
            st.session_state.authenticated = True
            st.session_state.current_page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")

def dashboard_page():
    st.markdown('<h1 class="main-header">🛡️ AI-IDPS Dashboard</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Packets", len(st.session_state.file_data) if st.session_state.file_data is not None else 0)
    with col2:
        st.metric("🚨 Threats", 0 if st.session_state.file_data is None else len(
            st.session_state.file_data[st.session_state.file_data["Threat_Score"] > 0.7]
        ))
    with col3:
        st.metric("🛡️ Status", "PROTECTED")

    if st.button("📂 File Scanner"):
        st.session_state.current_page = "scanner"
        st.rerun()

def scanner_page():
    st.markdown('<h1 class="main-header">📂 File Scanner</h1>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.session_state.file_data = df
        st.success("File loaded")

    if st.button("🚨 Load Built-in Dataset"):
        st.session_state.file_data = st.session_state.builtin_dataset
        st.success("Built-in dataset loaded")

    if st.session_state.file_data is not None:
        st.dataframe(st.session_state.file_data.head(10), use_container_width=True)

# ================= ROUTER =================
if not st.session_state.authenticated:
    if st.session_state.current_page == "login":
        login_page()
    else:
        about_page()
else:
    if st.session_state.current_page == "scanner":
        scanner_page()
    else:
        dashboard_page()
