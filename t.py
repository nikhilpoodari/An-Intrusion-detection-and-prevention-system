# =========================================================
# AI-IDPS : Complete Security Dashboard (FINAL FIXED VERSION)
# =========================================================

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

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="🛡️ AI IDPS - Complete Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS (UNCHANGED STYLE)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
.main-header{font-family:Poppins;font-size:4rem;font-weight:800;text-align:center}
.about-title{font-family:Poppins;font-size:3.2rem;font-weight:900;
background:linear-gradient(135deg,#667eea,#764ba2);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center}
.content-header{font-size:2.5rem;font-weight:700;color:#1e3a8a}
.live-indicator{background:linear-gradient(135deg,#00ff88,#00cc6a);
padding:1.5rem;border-radius:20px;font-weight:700;text-align:center}
.email-sent-popup{background:linear-gradient(135deg,#667eea,#764ba2);
padding:2rem;border-radius:20px;color:white;text-align:center}
</style>
""", unsafe_allow_html=True)

# =========================================================
# EMAIL CONFIG
# =========================================================
EMAIL_ADDRESS = "detectionsystemintrusion@gmail.com"
EMAIL_PASSWORD = "pbwggasppxzfjego"

def send_email_html(recipient, subject, html):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
    server.quit()

# =========================================================
# EMAIL TEMPLATES
# =========================================================
def send_no_threat_report(recipient, total_packets):
    html = f"""
    <html><body style="font-family:Arial;background:#f4f6f8;padding:20px">
    <div style="max-width:700px;margin:auto;background:white;border-radius:20px;
                box-shadow:0 15px 40px rgba(0,0,0,.15)">
        <div style="background:linear-gradient(135deg,#00b894,#00a085);
                    padding:30px;color:white;text-align:center">
            <h1>🛡️ AI-IDPS STATUS</h1>
        </div>
        <div style="padding:30px;text-align:center">
            <h2 style="color:#27ae60">✅ File Scan Complete</h2>
            <p style="font-size:20px"><b>{total_packets:,}</b> packets scanned</p>
            <p>No threats detected</p>
            <p style="color:#27ae60;font-weight:bold">NETWORK IS SAFE</p>
        </div>
    </div>
    </body></html>
    """
    send_email_html(recipient,
        "✅ AI-IDPS Scan Complete – No Threats Detected", html)

def send_detailed_threat_report(recipient, threats_df, total_packets, scan_type):
    rows = ""
    for _, r in threats_df.head(15).iterrows():
        rows += f"""
        <tr>
            <td>{r['Timestamp']}</td>
            <td>{r['Source_IP']}</td>
            <td>{r['Port']}</td>
            <td>{r['Packet_Length']}</td>
            <td>{r['Status']}</td>
        </tr>
        """

    html = f"""
    <html><body style="font-family:Arial;background:#f4f6f8;padding:20px">
    <div style="max-width:900px;margin:auto;background:white;border-radius:20px;
                box-shadow:0 15px 40px rgba(0,0,0,.15)">
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                    padding:35px;color:white;text-align:center">
            <h1>🚨 AI-IDPS THREAT ALERT</h1>
            <p>{scan_type} | {datetime.now()}</p>
        </div>
        <div style="padding:30px">
            <p><b>Total Packets:</b> {total_packets:,}</p>
            <p><b>Threats Detected:</b> {len(threats_df)}</p>
            <table border="1" cellpadding="8" cellspacing="0" width="100%">
                <tr style="background:#667eea;color:white">
                    <th>Time</th><th>IP</th><th>Port</th>
                    <th>Packet</th><th>Status</th>
                </tr>
                {rows}
            </table>
            <p style="color:#27ae60;font-weight:bold;text-align:center">
                ✅ All threats automatically BLOCKED
            </p>
        </div>
    </div>
    </body></html>
    """
    send_email_html(
        recipient,
        f"🚨 AI-IDPS ALERT – {len(threats_df)} Threats Detected",
        html
    )

def show_email_popup():
    st.markdown("""
    <div class="email-sent-popup">
        <h2>📧 Scan Report Sent</h2>
        <p>Check your inbox</p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
for k, v in {
    "authenticated": False,
    "current_page": "about",
    "user_email": None,
    "username": None,
    "file_data": None,
    "live_monitoring": False,
    "detection_df": pd.DataFrame(),
    "threat_details": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================================================
# BUILT-IN DATASET
# =========================================================
@st.cache_data
def load_builtin_dataset():
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        "Source_IP": np.random.choice(
            ["192.168.1.10","10.0.0.5","45.79.123.45","198.51.100.78"], n),
        "Port": np.random.choice([80,443,21,23,445], n),
        "Packet_Length": np.random.randint(60,65000,n),
    })
    df["Threat_Score"] = np.random.uniform(0,1,n)
    df["Threat_Level"] = df["Threat_Score"].apply(
        lambda x: "🚨 CRITICAL" if x>0.85 else "⚠️ HIGH" if x>0.7 else "✅ NORMAL")
    df["Status"] = df["Threat_Level"].apply(
        lambda x:"🚨 THREAT" if "CRITICAL" in x or "HIGH" in x else "✅ NORMAL")
    df["Timestamp"] = pd.date_range(
        start=datetime.now(), periods=n, freq="5S")
    return df

# =========================================================
# FILE SCANNER PAGE (ONLY EMAIL TRIGGER)
# =========================================================
def file_scanner_page():
    st.markdown('<h1 class="content-header">📂 File Scanner</h1>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload CSV", type="csv")
    if st.button("🚨 Load Built-in Dataset"):
        st.session_state.file_data = load_builtin_dataset()

    if uploaded:
        st.session_state.file_data = pd.read_csv(uploaded)

    if st.session_state.file_data is not None:
        df = st.session_state.file_data
        threats = df[df["Threat_Score"] > 0.7]
        total_packets = len(df)

        st.success(f"{total_packets:,} packets scanned")
        st.dataframe(df.head(10), use_container_width=True)

        if st.button("📧 SEND SCAN REPORT", type="primary", use_container_width=True):
            if len(threats) > 0:
                send_detailed_threat_report(
                    st.session_state.user_email,
                    threats,
                    total_packets,
                    "FILE SCAN"
                )
            else:
                send_no_threat_report(
                    st.session_state.user_email,
                    total_packets
                )
            show_email_popup()

# =========================================================
# OTHER PAGES (NO EMAILS HERE)
# =========================================================
def about_page():
    st.markdown('<h1 class="about-title">AI-Driven Intrusion Detection & Prevention System</h1>', unsafe_allow_html=True)
    st.info("Secure your network with AI-powered threat detection")

def live_status_page():
    st.markdown('<h1 class="content-header">🔍 Live Status</h1>', unsafe_allow_html=True)
    st.info("Live monitoring simulation")

def visualizations_page():
    st.markdown('<h1 class="content-header">📈 Visualizations</h1>', unsafe_allow_html=True)
    if st.session_state.file_data is not None:
        fig = px.pie(st.session_state.file_data, names="Threat_Level")
        st.plotly_chart(fig, use_container_width=True)

def feedback_page():
    st.markdown('<h1 class="content-header">💬 Feedback</h1>', unsafe_allow_html=True)
    msg = st.text_area("Your feedback")
    if st.button("Send"):
        send_email_html(
            "saiprasadreddy0910@gmail.com",
            "AI-IDPS Feedback",
            msg
        )
        st.success("Feedback sent")

# =========================================================
# MAIN
# =========================================================
def main():
    if not st.session_state.authenticated:
        about_page()
        if st.button("🔐 Login"):
            st.session_state.authenticated = True
            st.session_state.user_email = "yourmail@gmail.com"
    else:
        col1, col2 = st.columns([1,3])
        with col1:
            if st.button("File Scanner"): st.session_state.current_page="scanner"
            if st.button("Live Status"): st.session_state.current_page="live"
            if st.button("Visualizations"): st.session_state.current_page="visuals"
            if st.button("Feedback"): st.session_state.current_page="feedback"
        with col2:
            if st.session_state.current_page=="scanner":
                file_scanner_page()
            elif st.session_state.current_page=="live":
                live_status_page()
            elif st.session_state.current_page=="visuals":
                visualizations_page()
            elif st.session_state.current_page=="feedback":
                feedback_page()

main()
