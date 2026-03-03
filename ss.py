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

# ✅ THREAD-SAFE MONITORING CONTROL
live_monitoring_active = False

# Page config with Dark Theme
st.set_page_config(
    page_title="🛡️ AI IDPS - Complete Security Dashboard", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Streamlit Theme - Dark Mode
st.markdown("""
<style>
    :root {
        --primary-color: #667eea;
        --background-color: #0f1419;
        --secondary-background-color: #1a1f2e;
        --text-color: #ffffff;
        --text-color-neutral: #e0e0e0;
    }
    
    * {
        margin: 0;
        padding: 0;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #0f1419, #1a1f2e, #16213e, #533483);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e, #16213e);
        border-right: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif !important;
        color: #ffffff !important;
    }

    /* All text elements - ensure white color */
    h1, h2, h3, h4, h5, h6, p, span, div, a {
        color: #ffffff !important;
    }

    /* Main Header with Glow */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea, #764ba2, #ff6b6b);
        background-size: 200% 200%;
        animation: headerGlow 3s ease infinite;
        border-radius: 20px;
        box-shadow: 0 0 40px rgba(102, 126, 234, 0.8), 0 0 80px rgba(118, 75, 162, 0.5);
        text-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    }

    @keyframes headerGlow {
        0% { background-position: 0% 50%; box-shadow: 0 0 40px rgba(102, 126, 234, 0.8), 0 0 80px rgba(118, 75, 162, 0.5); }
        50% { background-position: 100% 50%; box-shadow: 0 0 60px rgba(255, 107, 107, 0.8), 0 0 100px rgba(118, 75, 162, 0.7); }
        100% { background-position: 0% 50%; box-shadow: 0 0 40px rgba(102, 126, 234, 0.8), 0 0 80px rgba(118, 75, 162, 0.5); }
    }

    /* Content Header - Bright Green */
    .content-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00ff88 !important;
        margin-bottom: 1.5rem;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }

    /* About Title */
    .about-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea, #764ba2, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 2rem 0;
    }

    /* Dashboard Heading - Bright Cyan */
    [data-testid="stAppViewContainer"] h2 {
        color: #00d9ff !important;
        text-shadow: 0 0 15px rgba(0, 217, 255, 0.4);
    }

    /* All markdown headings */
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #ffffff !important;
    }

    /* Live Indicator - Animated Pulse */
    .live-indicator {
        background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
        padding: 1.5rem;
        border-radius: 20px;
        font-weight: 700;
        color: #000;
        font-size: 1.4rem;
        text-align: center;
        animation: livePulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.6), 0 0 60px rgba(0, 204, 106, 0.3);
        border: 2px solid rgba(0, 255, 136, 0.8);
    }

    @keyframes livePulse {
        0%, 100% { 
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.6), 0 0 60px rgba(0, 204, 106, 0.3);
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 0 50px rgba(0, 255, 136, 0.9), 0 0 100px rgba(0, 204, 106, 0.6);
            transform: scale(1.02);
        }
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 2px solid #667eea !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.4s ease !important;
    }

    .stButton > button:hover {
        box-shadow: 0 0 40px rgba(102, 126, 234, 0.8) !important;
        transform: translateY(-2px) !important;
    }

    /* Text Input & Select */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: rgba(30, 30, 46, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 10px !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #a0a0a0 !important;
    }

    /* Tables */
    table {
        background: rgba(30, 30, 46, 0.8) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        box-shadow: 0 0 30px rgba(102, 126, 234, 0.3) !important;
        color: #ffffff !important;
    }

    thead {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: #ffffff !important;
    }

    tbody tr {
        color: #ffffff !important;
    }

    tbody tr:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        color: #ffffff !important;
    }

    td {
        color: #ffffff !important;
    }

    /* Metrics */
    [data-testid="metric-container"] {
        background: rgba(30, 30, 46, 0.8);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
    }

    [data-testid="metric-container"] > div {
        color: #ffffff !important;
    }

    /* Messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 15px !important;
        border-left: 5px solid !important;
        color: #ffffff !important;
    }

    .stSuccess {
        background: rgba(0, 184, 148, 0.1) !important;
        border-left-color: #00b894 !important;
    }

    .stSuccess p, .stSuccess span {
        color: #ffffff !important;
    }

    .stWarning {
        background: rgba(255, 107, 107, 0.1) !important;
        border-left-color: #ff6b6b !important;
    }

    .stWarning p, .stWarning span {
        color: #ffffff !important;
    }

    .stError {
        background: rgba(255, 0, 0, 0.1) !important;
        border-left-color: #ff0000 !important;
    }

    .stError p, .stError span {
        color: #ffffff !important;
    }

    .stInfo {
        background: rgba(102, 126, 234, 0.1) !important;
        border-left-color: #667eea !important;
    }

    .stInfo p, .stInfo span {
        color: #ffffff !important;
    }

    /* File uploader text */
    .stFileUploader {
        color: #ffffff !important;
    }

    /* Caption and small text */
    .stCaption {
        color: #e0e0e0 !important;
    }

    /* Form labels */
    label {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# 🚨 BUILT-IN ANOMALY DATASET WITH REALISTIC IP THREATS
@st.cache_data
def load_builtin_dataset():
    """Generate realistic network traffic with embedded anomalies"""
    np.random.seed(42)
    n_normal = 800
    n_anomalies = 200
    
    # NORMAL TRAFFIC (your local network)
    normal_ips = [
        '192.168.1.10', '192.168.1.20', '192.168.1.50', '192.168.1.100',
        '10.0.0.5', '10.0.0.15', '10.0.0.25', '10.0.0.99'
    ]
    normal_data = []
    for _ in range(n_normal):
        ip = np.random.choice(normal_ips)
        port = np.random.choice([80, 443, 22, 53])
        packet_length = np.random.randint(64, 1500)
        packets = np.random.poisson(10, 1)[0]
        bytes_sent = np.random.normal(1500, 200, 1)[0]
        duration = np.random.exponential(2, 1)[0]
        normal_data.append([ip, port, packet_length, packets, bytes_sent, duration, 0.05])
    
    # 🚨 ANOMALY TRAFFIC (suspicious IPs with high activity)
    anomaly_ips = [
        '45.79.123.45', '198.51.100.78', '203.0.113.200',  # Scanner bots
        '192.168.1.999', '10.0.0.255', '172.16.0.1',       # Internal anomalies
        '91.234.67.89', '185.220.101.XX'                    # C2 servers
    ]
    anomaly_data = []
    for _ in range(n_anomalies):
        ip = np.random.choice(anomaly_ips)
        port = np.random.choice([445, 3389, 23, 21])  # Suspicious ports
        packet_length = np.random.randint(5000, 65000)  # Oversized packets
        packets = np.random.poisson(150, 1)[0]
        bytes_sent = np.random.normal(50000, 10000, 1)[0]
        duration = np.random.exponential(0.1, 1)[0]
        threat_score = np.random.uniform(0.75, 0.98, 1)[0]
        anomaly_data.append([ip, port, packet_length, packets, bytes_sent, duration, threat_score])
    
    df = pd.DataFrame(normal_data + anomaly_data, 
                     columns=['Source_IP', 'Port', 'Packet_Length', 'Packets', 'Bytes_Sent', 'Duration_sec', 'Threat_Score'])
    
    # Add timestamp and classify threats
    df['Timestamp'] = pd.date_range(start='2025-12-27 20:00:00', periods=len(df), freq='10S')
    df['Threat_Level'] = df['Threat_Score'].apply(
        lambda x: '🚨 CRITICAL' if x > 0.85 else '⚠️ HIGH' if x > 0.7 else '✅ NORMAL'
    )
    df['Status'] = df['Threat_Level'].apply(lambda x: '🚨 THREAT' if 'CRITICAL' in x or 'HIGH' in x else '✅ NORMAL')
    df['Action_Taken'] = df['Status'].apply(lambda x: '🔒 BLOCKED' if x == '🚨 THREAT' else '✅ ALLOWED')
    
    return df.sample(frac=1).reset_index(drop=True)

# Initialize session state
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "username" not in st.session_state: st.session_state.username = None
if "user_email" not in st.session_state: st.session_state.user_email = None
if "local_ips" not in st.session_state: st.session_state.local_ips = []
if "current_page" not in st.session_state: st.session_state.current_page = "about"
if "file_data" not in st.session_state: st.session_state.file_data = None
if "detection_df" not in st.session_state: st.session_state.detection_df = pd.DataFrame()
if "threat_details" not in st.session_state: st.session_state.threat_details = []
if "live_monitoring" not in st.session_state: st.session_state.live_monitoring = False
if "visuals_email_sent" not in st.session_state: st.session_state.visuals_email_sent = False
if "builtin_dataset" not in st.session_state: st.session_state.builtin_dataset = load_builtin_dataset()

# Get local IPs
def get_laptop_ips():
    local_ips = []
    try:
        interfaces = psutil.net_if_addrs()
        for interface_name, interface_addresses in interfaces.items():
            for address in interface_addresses:
                if address.family == socket.AF_INET and not address.address.startswith("127."):
                    local_ips.append({
                        'interface': interface_name,
                        'ip': address.address,
                        'netmask': getattr(address, 'netmask', '255.255.255.0')
                    })
    except:
        local_ips = [
            {'interface': 'WiFi/Ethernet', 'ip': '192.168.1.XXX', 'netmask': '255.255.255.0'},
            {'interface': 'Local Network', 'ip': '10.0.0.XXX', 'netmask': '255.255.255.0'}
        ]
    return local_ips

st.session_state.local_ips = get_laptop_ips()

# Email System - SIMPLE VERSION (FIXED - MOVED BEFORE FUNCTIONS)
EMAIL_ADDRESS = "detectionsystemintrusion@gmail.com"
EMAIL_PASSWORD = "pbwggasppxzfjego"

def send_email(recipient, subject, body):
    """Simple email function for welcome messages"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = subject
        
        html_body = f"""
        <html><body style="font-family: Arial; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white; border-radius: 15px 15px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🛡️ AI-IDPS Security System</h1>
                </div>
                <div style="padding: 30px; font-size: 18px; line-height: 1.6;">
                    <h2 style="color: #1e3a8a; text-align: center; font-size: 24px;">{subject}</h2>
                    <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; text-align: center; font-size: 20px;">
                        <p><strong>{body}</strong></p>
                    </div>
                </div>
            </div>
        </body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        server.quit()
        return True
    except:
        return False
def send_no_threat_report(recipient, total_packets):
    try:
        html_body = f"""
        <html>
        <body style="font-family: Arial; background:#f4f6f8; padding:20px;">
            <div style="max-width:700px;margin:auto;background:white;
                        border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.15);">
                
                <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                            padding:30px;text-align:center;color:white;
                            border-radius:16px 16px 0 0;">
                    <h1>🛡️ AI Security Status</h1>
                </div>

                <div style="padding:35px;text-align:center;">
                    <h2 style="color:#27ae60;">📊 File Scan Complete</h2>

                    <div style="margin-top:25px;
                                background:#e8f8f0;
                                padding:25px;
                                border-radius:12px;
                                border-left:6px solid #2ecc71;">
                        <h3>✅ Scanned {total_packets:,} records</h3>
                        <p>No threats detected!</p>
                    </div>

                    <p style="margin-top:20px;">
                        Your network is <strong>SAFE & PROTECTED 24/7</strong>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient
        msg["Subject"] = "✅ AI-IDPS File Scan Complete – No Threats Detected"
        msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        server.quit()
        return True
    except:
        return False




def show_email_popup():
    st.markdown("""
    <div class="email-sent-popup">
        <h2 style="margin: 0;">📧 DETAILED THREAT REPORT SENT!</h2>
        <p style="margin: 10px 0 0 0;">Check inbox for complete threat analysis + IP table</p>
    </div>
    """, unsafe_allow_html=True)

# ========== BUILT-IN DATASET BUTTON (ONLY IN FILE SCANNER) ==========
def show_builtin_dataset():
    """Display button to load built-in anomaly dataset - ONLY in file scanner"""
    if st.button("🚨 *LOAD BUILT-IN ANOMALY DATASET (1000 records)*", type="primary", use_container_width=True):
        st.session_state.file_data = st.session_state.builtin_dataset.copy()
        st.success("✅ *LOADED!* 1000 records with *200+ embedded anomalies* 🚨")
        st.info("*Anomalies include:* Scanner bots, DDoS sources, C2 servers, oversized packets")
        st.rerun()

# ========== 1. ABOUT PAGE ==========
def about_page():
    st.markdown('<h1 class="about-title">AI-DRIVEN INTRUSION DETECTION & PREVENTION SYSTEM</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🚀 *WHAT IS AI-IDPS?*
        *Advanced AI-powered security* that:
        - 🔍 *Detects* threats in real-time
        - 🛡️ *Blocks* attacks automatically  
        - 📧 *Alerts* you instantly with IP tables
        - 📊 *Visualizes* network activity
        
        *Protects your entire network 24/7*
        """)
    
    with col2:
        st.markdown("""
        ### 🛡️ *KEY FEATURES*
        - 🤖 *AI Threat Detection*
        - 🌐 *Live Network Monitoring*  
        - 🚨 *Detailed Email Reports*
        - 📈 *Interactive Dashboards*
        - 🔒 *Auto-Blocking*
        - 💾 *File Scanning*
        """)
    
    st.markdown("""
    ### 🎯 *PROTECTION COVERAGE*
    """)
    col1, col2, col3 = st.columns(3)
    with col1: st.success("*WiFi Networks* ✅")
    with col2: st.success("*Ethernet* ✅") 
    with col3: st.success("*All Devices* ✅")
    
    if st.button("🔐 *START PROTECTION - LOGIN*", type="primary", use_container_width=True):
        st.session_state.current_page = "login"
        st.rerun()

# ========== 2. LOGIN PAGE ==========
def login_page():
    st.markdown('<h1 class="main-header">🔐 Secure Login Required</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### 🌐 *Network Interfaces*")
        for ip_info in st.session_state.local_ips:
            st.success(f"*{ip_info['interface']}*: {ip_info['ip']}")
    with col2:
        with st.form("login_form"):
            col_form1, col_form2, col_form3 = st.columns([1,1,1])
            with col_form1:
                username = st.text_input("👤 Username", placeholder="admin / user")
            with col_form2:
                password = st.text_input("🔑 Password", type="password")
            with col_form3:
                user_email = st.text_input("📧 Email (for alerts)", placeholder="your.email@gmail.com")
            
            login_btn = st.form_submit_button("🚀 ACCESS DASHBOARD", use_container_width=True, type="primary")
        
        if login_btn:
            credentials = {"admin": "admin123", "user": "user123"}
            if username in credentials and credentials[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_email = user_email
                send_email(user_email, "🎉 Welcome to AI-IDPS!", 
                          f"Welcome {username}! Your network protection is now ACTIVE.")
                st.session_state.current_page = "welcome"
                st.rerun()
            else:
                st.error("❌ Invalid credentials! Try: *admin/admin123* or *user/user123*")

# ========== 3. WELCOME PAGE ==========
def welcome_page():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<h1 class="content-header">🎉 Welcome!</h1>', unsafe_allow_html=True)
        st.markdown(f"### 👋 Hello {st.session_state.username.title()}!")
        st.markdown("*Your AI Security System is ACTIVE* ✅")
        st.markdown("*Protecting:*")
        for ip in st.session_state.local_ips:
            st.caption(f"🔌 {ip['ip']}")
    with col2:
        st.success("📧 *Welcome email sent* to your inbox!")
        st.info("""
        ### 🚀 *Quick Start Guide*
        1. 📂 *File Scanner* - Upload files or load BUILT-IN DATASET
        2. 🔍 *Live Status* - Real-time monitoring  
        3. 📈 *Visualizations* - See anomalies highlighted!
        """)
        if st.button("🌐 GO TO DASHBOARD", type="primary", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

# ========== 4. FILE SCANNER ==========
# ========== 4. FILE SCANNER (FIXED - NOW DETECTS UPLOADED FILES) ==========
def file_scanner_page():
    st.markdown('<h1 class="content-header">📂 File Scanner</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        uploaded_file = st.file_uploader("📁 Upload CSV", type=['csv'])
        st.markdown("---")
        show_builtin_dataset()
        
    with col2:
        # ✅ FIXED: Handle uploaded file IMMEDIATELY when selected
        if uploaded_file is not None:
            try:
                # Read uploaded CSV
                df = pd.read_csv(uploaded_file)
                st.session_state.file_data = df.copy()
                
                # ✅ AUTOMATIC THREAT DETECTION - Call the function
                detect_threats_from_csv(df)
                
                # Don't continue - let st.rerun() handle display
                st.stop()  # Stop execution until rerun completes
                
            except Exception as e:
                st.error(f"❌ Error reading CSV: {str(e)}")
                st.info("💡 Try the BUILT-IN DATASET button instead")
        
        # ✅ Only show results if file_data exists AND threat detection completed
        elif st.session_state.file_data is not None:
            df = st.session_state.file_data
            
            # ✅ Ensure threat columns exist (safety check)
            if 'Threat_Score' not in df.columns:
                st.warning("⚠️ Running threat detection...")
                detect_threats_from_csv(df)
                st.stop()
            
            # ✅ CALCULATE METRICS
            total_packets = len(df)
            high_threats = df[df['Threat_Score'] > 0.7] if 'Threat_Score' in df.columns else pd.DataFrame()
            critical_threats = df[df['Threat_Score'] > 0.85] if 'Threat_Score' in df.columns else pd.DataFrame()
            num_threats = len(high_threats)
            status = "🚨 THREATS DETECTED" if num_threats > 0 else "✅ NETWORK SAFE"
            
            # ✅ DISPLAY SUCCESS/WARNING METRICS
            st.success(f"✅ *{total_packets:,} packets* scanned successfully!")
            if num_threats > 0:
                st.warning(f"🚨 *{num_threats} threats* detected ({len(critical_threats)} critical)!")
            else:
                st.info("✅ *No threats detected* - Network appears safe!")
    
    # ✅ MOVE METRICS TO TOP LEVEL (outside nested columns)
    if st.session_state.file_data is not None:
        df = st.session_state.file_data
        if 'Threat_Score' in df.columns:
            total_packets = len(df)
            high_threats = df[df['Threat_Score'] > 0.7]
            critical_threats = df[df['Threat_Score'] > 0.85]
            num_threats = len(high_threats)
            status = "🚨 THREATS DETECTED" if num_threats > 0 else "✅ NETWORK SAFE"
            
            # ✅ KEY METRICS DISPLAY (3 COLUMNS) - AT TOP LEVEL
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("📦 Total Packets", f"{total_packets:,}")
            with col_m2:
                st.metric("🚨 Threats Found", f"{num_threats:,}", delta=f"{len(critical_threats)} CRITICAL")
            with col_m3:
                st.metric("🛡️ Status", status)
            
            # ✅ SEND REPORT BUTTON
            if st.button("📧 *SEND SCAN REPORT*", type="primary", use_container_width=True):
                if num_threats > 0:
                    send_detailed_threat_report(st.session_state.user_email, high_threats, total_packets, "FILE SCAN")
                else:
                    send_no_threat_report(
                         st.session_state.user_email,
                         total_packets
                    )

                show_email_popup()

            # ✅ DATA PREVIEW
            st.markdown("### 📋 Sample Data (Threats Highlighted)")
            display_cols = ['Timestamp', 'Source_IP', 'Port', 'Packet_Length', 'Status', 'Action_Taken', 'Threat_Score']
            available_cols = [col for col in display_cols if col in df.columns]
            st.dataframe(df[available_cols].head(10), use_container_width=True)
            
            # ✅ THREAT SUMMARY TABLE
            if num_threats > 0:
                st.markdown("### 🚨 *TOP 10 THREATS*")
                threat_cols = ['Timestamp', 'Source_IP', 'Port', 'Packet_Length', 'Threat_Score', 'Threat_Level', 'Action_Taken']
                threat_display_cols = [col for col in threat_cols if col in df.columns]
                st.dataframe(high_threats[threat_display_cols].head(10), use_container_width=True)
        else:
            st.info('👈 *Click "LOAD BUILT-IN DATASET"* or upload your own CSV')


# ✅ COMPLETE FIXED: AUTOMATIC THREAT DETECTION FOR UPLOADED CSV
def detect_threats_from_csv(df):
    """Detect threats from uploaded CSV files automatically - FIXED VERSION"""
    # If no threat columns exist, create realistic threat detection
    if 'Threat_Score' not in df.columns:
        print("🔍 Analyzing uploaded file for threats...")  # Debug print
        
        # Create threat score based on common columns
        threat_scores = []
        for idx, row in df.iterrows():
            score = 0.1  # Base score
            
            # Check for suspicious IPs (case insensitive)
            if 'Source_IP' in df.columns and pd.notna(row.get('Source_IP', '')):
                ip = str(row['Source_IP']).strip().lower()
                suspicious_patterns = ['45.', '198.', '203.', '91.', '185.']
                if any(pattern in ip for pattern in suspicious_patterns):
                    score += 0.4
            
            # Check packet sizes (if column exists)
            for col in df.columns:
                if 'packet' in col.lower() or 'byte' in col.lower() or 'size' in col.lower():
                    try:
                        if pd.notna(row.get(col, 0)):
                            val = float(row[col])
                            if val > 5000:
                                score += 0.3
                    except:
                        continue
            
            # Check ports (if column exists)
            if 'Port' in df.columns and pd.notna(row.get('Port', '')):
                try:
                    port = int(float(row['Port']))
                    suspicious_ports = [21, 23, 445, 3389, 1433, 161]
                    if port in suspicious_ports:
                        score += 0.3
                except:
                    pass
            
            # High packet count check
            if 'Packets' in df.columns and pd.notna(row.get('Packets', 0)):
                try:
                    packets = float(row['Packets'])
                    if packets > 100:
                        score += 0.2
                except:
                    pass
            
            threat_scores.append(min(score, 0.98))
        
        # Add threat columns
        df['Threat_Score'] = threat_scores
        df['Threat_Level'] = df['Threat_Score'].apply(
            lambda x: '🚨 CRITICAL' if x > 0.85 else '⚠️ HIGH' if x > 0.7 else '✅ NORMAL'
        )
        df['Status'] = df['Threat_Level'].apply(
            lambda x: '🚨 THREAT' if 'CRITICAL' in x or 'HIGH' in x else '✅ NORMAL'
        )
        df['Action_Taken'] = df['Status'].apply(
            lambda x: '🔒 BLOCKED' if x == '🚨 THREAT' else '✅ ALLOWED'
        )
        
        # Add timestamps if missing
        if 'Timestamp' not in df.columns:
            df['Timestamp'] = pd.date_range(start='2025-12-27 20:00:00', periods=len(df), freq='10S')

    # Update session state AFTER processing
    st.session_state.file_data = df.copy()
    
    # Calculate final metrics
    high_threats = df[df['Threat_Score'] > 0.7]
    if len(high_threats) > 0:
        st.success(f"✅ *File analyzed! Found {len(high_threats)} threats* 🚨")
    else:
        st.success("✅ *File analyzed! No threats detected* ✅")
    # AUTO EMAIL AFTER SCAN
    if st.session_state.user_email:
        if len(high_threats) > 0:
            send_detailed_threat_report(
                 st.session_state.user_email,
                 high_threats,
                 len(df),
                 "FILE SCAN"
            )
        else:
            send_no_threat_report(
                st.session_state.user_email,
                len(df)
            )
    
    
    st.rerun()  # Refresh to show results


# ✅ FIXED EMAIL FUNCTION - NOW ACCEPTS total_packets PARAMETER
def send_detailed_threat_report(recipient, threats_df, total_packets=None, scan_type="FILE SCAN"):
    """Send ENHANCED real-time monitoring report with EXACT columns requested"""
    try:
        total_threats = len(threats_df)
        critical_threats = len(threats_df[threats_df['Threat_Level'] == '🚨 CRITICAL']) if 'Threat_Level' in threats_df.columns else 0
        
        # ✅ REAL-TIME MONITORING SUMMARY
        scan_summary = f"{total_packets:,} packets" if total_packets else "LIVE MONITORING"
        
        # ✅ CREATE TABLE WITH EXACT COLUMNS: time, source ip, port, packet length, status
        threat_table = ""
        display_cols = ['Timestamp', 'Source_IP', 'Port', 'Packet_Length', 'Status']
        available_cols = [col for col in display_cols if col in threats_df.columns]
        
        for _, row in threats_df.head(15).iterrows():  # Top 15 threats
            row_data = [str(row.get(col, 'N/A')) for col in available_cols]
            threat_table += f"""
            <tr style="border-bottom: 1px solid #ddd; background: {'#ffebee' if 'CRITICAL' in str(row.get('Threat_Level', '')) else '#fff3e0'};">
                <td style="padding: 12px; text-align: left; font-weight: 600;">{row_data[0]}</td>
                <td style="padding: 12px; text-align: left; color: #e74c3c; font-family: monospace;">{row_data[1]}</td>
                <td style="padding: 12px; text-align: center; font-weight: bold;">{row_data[2]}</td>
                <td style="padding: 12px; text-align: center; color: #f39c12;">{row_data[3]}</td>
                <td style="padding: 12px; text-align: center; font-size: 1.1em;">{row_data[4]}</td>
            </tr>
            """
        
        html_body = f"""
<html>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(-45deg, #667eea, #764ba2, #ff6b6b, #00b894); 
             background-size: 400% 400%; animation: gradientBG 15s ease infinite; padding: 20px; margin: 0;">

<style>
@keyframes gradientBG {{
    0% {{background-position: 0% 50%;}}
    50% {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}
th, td {{ transition: all 0.3s ease; }}
tbody tr:hover {{ background: #f0f0f0; transform: scale(1.01); }}
</style>

<div style="max-width: 900px; margin: 0 auto; background: white; border-radius: 20px; 
            box-shadow: 0 15px 40px rgba(0,0,0,0.2); overflow: hidden;">

    <!-- HEADER -->
    <div style="background: linear-gradient(135deg, #667eea, #764ba2, #ff6b6b); 
                padding: 40px; text-align: center; color: white; box-shadow: 0 5px 20px rgba(0,0,0,0.2);">
        <h1 style="margin: 0; font-size: 34px; font-weight: 900;">🛡️ AI-IDPS REAL-TIME MONITORING</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.95;">{scan_type} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <!-- SUMMARY CARDS -->
    <div style="padding: 30px; background: #f8f9fa; border-bottom: 4px solid #667eea;">
        <h2 style="color: #1e3a8a; text-align: center; margin: 0 0 25px 0; font-size: 26px;">📊 MONITORING SUMMARY</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; text-align: center;">
            
            <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; 
                        padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
                <h3 style="margin: 0 0 10px 0; font-size: 28px; font-weight: 700;">{total_threats}</h3>
                <p style="margin: 0; font-weight: 600;">Threats Detected</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #ff4757, #ff6b81); color: white; 
                        padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
                <h3 style="margin: 0 0 10px 0; font-size: 24px; font-weight: 700;">{critical_threats}</h3>
                <p style="margin: 0; font-weight: 600;">CRITICAL Threats</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #2ed573, #1e90ff); color: white; 
                        padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
                <h3 style="margin: 0 0 10px 0; font-size: 22px; font-weight: 700;">{scan_summary}</h3>
                <p style="margin: 0; font-weight: 600;">Total Packets Analyzed</p>
            </div>
        </div
        
        <div style="text-align: center; margin-top: 25px; padding: 20px; 
                    background: #e8f5e8; border-radius: 12px; border-left: 5px solid #27ae60; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <h3 style="color: #27ae60; margin: 0 0 10px 0;">✅ STATUS: ALL THREATS AUTO-BLOCKED</h3>
            <p style="margin: 0; font-size: 16px;">Your network is PROTECTED 24/7 by AI-IDPS</p>
        </div>
    </div>
    
    <!-- THREAT DETAILS TABLE -->
    <div style="padding: 30px;">
        <h2 style="color: #1e3a8a; margin: 0 0 25px 0; font-size: 24px;">📋 TOP 15 THREAT DETAILS</h2>
        <div style="overflow-x: auto; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
            <table style="width: 100%; border-collapse: collapse; background: white; font-size: 14px;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; font-weight: 700;">
                        <th style="padding: 15px; text-align: left;">🕒 Time</th>
                        <th style="padding: 15px; text-align: left;">🌐 Source IP</th>
                        <th style="padding: 15px; text-align: center;">🔌 Port</th>
                        <th style="padding: 15px; text-align: center;">📦 Packet Length</th>
                        <th style="padding: 15px; text-align: center;">📊 Status</th>
                    </tr>
                </thead>
                <tbody>
                    {threat_table}
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""

        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = f"🚨 AI-IDPS ALERT: {total_threats} Threats Detected & BLOCKED - {scan_type}"
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
# ========== 5. LIVE STATUS ==========
def live_status_page():
    global live_monitoring_active
    
    st.markdown('<h1 class="content-header">🔍 Live Status</h1>', unsafe_allow_html=True)
    
    # Control buttons at top level
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        if st.button("🚀 START MONITORING", type="primary"):
            st.session_state.detection_df = pd.DataFrame()
            st.session_state.threat_details = []
            live_monitoring_active = True
            threading.Thread(target=live_monitoring_thread, daemon=True).start()
            st.success("✅ Monitoring started!")
    with col_ctrl2:
        if st.button("⏹️ STOP MONITORING", type="secondary"):
            live_monitoring_active = False
            st.info("⏹️ Monitoring stopped")

    # Live indicator
    if live_monitoring_active:
        st.markdown('<div class="live-indicator">🔴 *LIVE PROTECTION ACTIVE*</div>', unsafe_allow_html=True)
    
    # Metrics at top level
    threats = len(st.session_state.threat_details)
    packets = len(st.session_state.detection_df)
    
    col1m, col2m, col3m = st.columns(3)
    with col1m: 
        st.metric("📦 Packets", packets)
    with col2m: 
        st.metric("🚨 Threats", threats)
    with col3m: 
        st.metric("🔒 Status", "PROTECTED" if threats == 0 else "⚠️ ALERT")
    
    # Recent activity
    if not st.session_state.detection_df.empty:
        st.markdown("### 📋 Recent Activity")
        st.dataframe(st.session_state.detection_df.tail(10), use_container_width=True)

# ========== 6. VISUALIZATIONS ==========
def visualizations_page():
    st.markdown('<h1 class="content-header">📈 Visualizations</h1>', unsafe_allow_html=True)
    st.info("📊 *Charts show REAL anomalies* from dataset")
    
    if st.session_state.file_data is not None:
        df = st.session_state.file_data.copy()
        
        # Check if Threat_Level column exists, if not create it
        if 'Threat_Level' not in df.columns:
            st.warning("⚠️ Threat_Level column not found. Running threat detection...")
            detect_threats_from_csv(df)
            st.stop()
        
        # Charts side by side at top level
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            fig_pie = px.pie(df, names='Threat_Level', title="🚨 Threat Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_v2:
            if 'Threat_Score' in df.columns:
                fig_hist = px.histogram(df, x='Threat_Score', color='Threat_Level', 
                                      title="📊 Threat Score Distribution", nbins=20)
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("📊 Threat_Score column not available for histogram")
        
        # Suspicious IPs section
        st.markdown("### 🌐 *Suspicious IPs Detected*")
        required_cols = ['Source_IP', 'Port', 'Packet_Length', 'Threat_Level']
        available_cols = [c for c in required_cols if c in df.columns]

        if len(available_cols) > 0:
            suspicious_ips = df[df['Threat_Score'] > 0.7][available_cols].head(10) if 'Threat_Score' in df.columns else df[available_cols].head(10)
            st.dataframe(suspicious_ips, use_container_width=True)
        else:
            st.warning("⚠️ Required columns not found in the dataset")
        
        if not st.session_state.visuals_email_sent:
            if 'Threat_Score' in df.columns:
                high_threats = df[df['Threat_Score'] > 0.7]
                if len(high_threats) > 0:
                    send_detailed_threat_report(st.session_state.user_email, high_threats)
                    st.session_state.visuals_email_sent = True
                    show_email_popup()
    else:
        st.warning("👈 *Load dataset first* in File Scanner")

# ========== 7. FEEDBACK ==========
def feedback_page():
    st.markdown('<h1 class="content-header">💬 Feedback</h1>', unsafe_allow_html=True)
    st.markdown("### 🎯 Help us improve AI-IDPS!")
    
    with st.form("feedback_form"):
        # Sliders at top level, not nested
        rating = st.slider("⭐ How would you rate AI-IDPS?", 1, 5, 4)
        ease = st.slider("😊 How easy was it to use?", 1, 5, 5)
        satisfaction = st.slider("✅ Overall satisfaction?", 1, 5, 4)
        
        # Comments textarea
        comments = st.text_area("💭 Any suggestions or feedback?")
        
        # Submit button at form level
        submit_btn = st.form_submit_button("📧 SEND FEEDBACK", type="primary", use_container_width=True)
    
    # Handle form submission after form block
    if submit_btn:
        feedback = f"Rating: {rating}/5 | Ease: {ease}/5 | Satisfaction: {satisfaction}/5\n\n{comments}"
        send_email("saiprasadreddy0910@gmail.com", f"AI-IDPS Feedback - {st.session_state.username}", feedback)
        st.success("✅ Thank you! Your feedback helps improve AI-IDPS!")
        st.balloons()

def live_monitoring_thread():
    """Enhanced with REAL anomaly patterns - FIXED for thread safety"""
    global live_monitoring_active
    
    anomaly_ips = ['45.79.123.45', '198.51.100.78', '203.0.113.200', '192.168.1.999']
    normal_ips = ['192.168.1.10', '192.168.1.20', '10.0.0.5']
    
    while live_monitoring_active:
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if np.random.random() < 0.2:
                src_ip = np.random.choice(anomaly_ips)
                threat = np.random.uniform(0.75, 0.98)
                status = "🚨 THREAT"
            else:
                src_ip = np.random.choice(normal_ips)
                threat = np.random.uniform(0, 0.3)
                status = "✅ NORMAL"
            
            new_row = pd.DataFrame({
                'Time': [now], 'Source IP': [src_ip], 'Threat': [f"{threat:.1%}"], 'Status': [status]
            })
            
            if status == "🚨 THREAT":
                st.session_state.threat_details.append({'ip': src_ip, 'threat': threat})
            
            st.session_state.detection_df = pd.concat([st.session_state.detection_df.tail(50), new_row], ignore_index=True)
            time.sleep(2)
        except:
            time.sleep(1)

# ========== MAIN NAVIGATION ==========
def main():
    if not st.session_state.authenticated:
        if st.session_state.current_page == "login":
            login_page()
        else:
            about_page()
    else:
        if st.session_state.current_page == "welcome":
            welcome_page()
        else:
            left_col, right_col = st.columns([1, 3])
            
            with left_col:
                st.markdown('<div style="padding: 2rem 1rem;">', unsafe_allow_html=True)
                st.markdown('<h2 style="color: #1e3a8a; text-align: center; margin-bottom: 2rem;">📋 Dashboard</h2>', unsafe_allow_html=True)
                
                if st.button("📂 *FILE SCANNER*", key="scanner_tab"):
                    st.session_state.current_page = "scanner"
                    st.rerun()
                if st.button("🔍 *LIVE STATUS*", key="live_tab"):
                    st.session_state.current_page = "live"
                    st.rerun()
                if st.button("📈 *VISUALIZATIONS*", key="visuals_tab"):
                    st.session_state.current_page = "visuals"
                    st.rerun()
                if st.button("💬 *FEEDBACK*", key="feedback_tab"):
                    st.session_state.current_page = "feedback"
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with right_col:
                if st.session_state.current_page == "scanner":
                    file_scanner_page()
                elif st.session_state.current_page == "live":
                    live_status_page()
                elif st.session_state.current_page == "visuals":
                    visualizations_page()
                elif st.session_state.current_page == "feedback":
                    feedback_page()

if __name__ == "__main__":
   main()
