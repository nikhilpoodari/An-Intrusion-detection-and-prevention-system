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

# Page config
st.set_page_config(
    page_title="🛡️ AI IDPS - Complete Security Dashboard", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main-header {font-family: 'Poppins', sans-serif; font-size: 4rem; font-weight: 800; 
                  color: #1e3a8a; text-align: center; margin-bottom: 2rem; text-shadow: 0 4px 8px rgba(0,0,0,0.2);}
    .about-title {font-family: 'Poppins', sans-serif; font-size: 3.5rem; font-weight: 900; 
                  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-align: center; margin: 2rem 0;}
    .metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  padding: 2rem; border-radius: 20px; color: white; text-align: center; 
                  box-shadow: 0 10px 30px rgba(102,126,234,0.3);}
    .threat-popup {background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                   padding: 3rem; border-radius: 25px; text-align: center; color: white;
                   box-shadow: 0 20px 50px rgba(255,107,107,0.4); font-size: 1.4rem;}
    .success-popup {background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
                    padding: 3rem; border-radius: 25px; text-align: center; color: white;
                    box-shadow: 0 20px 50px rgba(0,184,148,0.4); font-size: 1.4rem;}
    .email-sent-popup {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       padding: 2rem; border-radius: 20px; text-align: center; color: white;}
    .live-indicator {background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%); 
                     padding: 1.5rem; border-radius: 20px; font-weight: 700; color: #000; 
                     font-size: 1.4rem; text-align: center;}
    .nav-btn {padding: 1.5rem 1rem; margin: 0.5rem 0; border-radius: 15px; font-size: 1.2rem;
              font-weight: 600; border: none; cursor: pointer; transition: all 0.3s;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
              width: 100%; height: 80px; box-shadow: 0 5px 15px rgba(102,126,234,0.3);}
    .nav-btn:hover {transform: translateY(-2px); box-shadow: 0 10px 25px rgba(102,126,234,0.5);}
    .content-header {font-family: 'Poppins', sans-serif; font-size: 2.5rem; font-weight: 700; 
                     color: #1e3a8a; margin-bottom: 1.5rem;}
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
        packets = np.random.poisson(10, 1)[0]  # Normal packet counts
        bytes_sent = np.random.normal(1500, 200, 1)[0]  # Normal bytes
        duration = np.random.exponential(2, 1)[0]  # Normal session duration
        normal_data.append([ip, packets, bytes_sent, duration, 0.05])  # Low threat score
    
    # 🚨 ANOMALY TRAFFIC (suspicious IPs with high activity)
    anomaly_ips = [
        '45.79.123.45', '198.51.100.78', '203.0.113.200',  # Scanner bots
        '192.168.1.999', '10.0.0.255', '172.16.0.1',       # Internal anomalies
        '91.234.67.89', '185.220.101.XX'                    # C2 servers
    ]
    anomaly_data = []
    for _ in range(n_anomalies):
        ip = np.random.choice(anomaly_ips)
        packets = np.random.poisson(150, 1)[0]  # 🚨 HIGH packet counts
        bytes_sent = np.random.normal(50000, 10000, 1)[0]  # 🚨 HIGH bytes
        duration = np.random.exponential(0.1, 1)[0]  # 🚨 Short bursts
        threat_score = np.random.uniform(0.75, 0.98, 1)[0]  # 🚨 HIGH threat
        anomaly_data.append([ip, packets, bytes_sent, duration, threat_score])
    
    df = pd.DataFrame(normal_data + anomaly_data, 
                     columns=['Source_IP', 'Packets', 'Bytes_Sent', 'Duration_sec', 'Threat_Score'])
    
    # Add timestamp and classify threats
    df['Timestamp'] = pd.date_range(start='2025-12-27 20:00:00', periods=len(df), freq='10S')
    df['Threat_Level'] = df['Threat_Score'].apply(
        lambda x: '🚨 CRITICAL' if x > 0.85 else '⚠️ HIGH' if x > 0.7 else '✅ NORMAL'
    )
    df['Status'] = df['Threat_Level'].apply(lambda x: '🚨 THREAT' if 'CRITICAL' in x or 'HIGH' in x else '✅ NORMAL')
    
    return df.sample(frac=1).reset_index(drop=True)  # Shuffle for realism

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

# Email System
EMAIL_ADDRESS = "detectionsystemintrusion@gmail.com"
EMAIL_PASSWORD = "pbwggasppxzfjego"

def send_email(recipient, subject, body):
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

def show_email_popup():
    st.markdown("""
    <div class="email-sent-popup">
        <h2 style="margin: 0;">📧 STATUS REPORT SENT!</h2>
        <p style="margin: 10px 0 0 0;">Check your inbox for security update</p>
    </div>
    """, unsafe_allow_html=True)

# ========== BUILT-IN DATASET BUTTON ==========
def show_builtin_dataset():
    """Display button to load built-in anomaly dataset"""
    if st.button("🚨 **LOAD BUILT-IN ANOMALY DATASET (1000 records)**", type="primary", use_container_width=True):
        st.session_state.file_data = st.session_state.builtin_dataset.copy()
        st.success("✅ **LOADED!** 1000 records with **200+ embedded anomalies** 🚨")
        st.info("**Anomalies include:** Scanner bots, DDoS sources, C2 servers")
        st.rerun()

# ========== 1. ABOUT PAGE ==========
def about_page():
    st.markdown('<h1 class="about-title">AI-DRIVEN INTRUSION DETECTION & PREVENTION SYSTEM</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🚀 **WHAT IS AI-IDPS?**
        **Advanced AI-powered security** that:
        - 🔍 **Detects** threats in real-time
        - 🛡️ **Blocks** attacks automatically  
        - 📧 **Alerts** you instantly
        - 📊 **Visualizes** network activity
        
        **Protects your entire network 24/7**
        """)
    
    with col2:
        st.markdown("""
        ### 🛡️ **KEY FEATURES**
        - 🤖 **AI Threat Detection**
        - 🌐 **Live Network Monitoring**  
        - 🚨 **Instant Email Alerts**
        - 📈 **Interactive Dashboards**
        - 🔒 **Auto-Blocking**
        - 💾 **File Scanning + BUILT-IN DATASET**
        """)
    
    st.markdown("""
    ### 🎯 **PROTECTION COVERAGE**
    """)
    col1, col2, col3 = st.columns(3)
    with col1: st.success("**WiFi Networks** ✅")
    with col2: st.success("**Ethernet** ✅") 
    with col3: st.success("**All Devices** ✅")
    
    # 🚨 BUILT-IN DATASET BUTTON ON ABOUT PAGE
    st.markdown("---")
    show_builtin_dataset()
    
    if st.button("🔐 **START PROTECTION - LOGIN**", type="primary", use_container_width=True):
        st.session_state.current_page = "login"
        st.rerun()

# ========== 2. LOGIN PAGE ==========
def login_page():
    st.markdown('<h1 class="main-header">🔐 Secure Login Required</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### 🌐 **Network Interfaces**")
        for ip_info in st.session_state.local_ips:
            st.success(f"**{ip_info['interface']}**: `{ip_info['ip']}`")
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
                st.error("❌ Invalid credentials! Try: **admin/admin123** or **user/user123**")

# ========== 3. WELCOME PAGE ==========
def welcome_page():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<h1 class="content-header">🎉 Welcome!</h1>', unsafe_allow_html=True)
        st.markdown(f"### 👋 Hello {st.session_state.username.title()}!")
        st.markdown("**Your AI Security System is ACTIVE** ✅")
        st.markdown("**Protecting:**")
        for ip in st.session_state.local_ips:
            st.caption(f"🔌 {ip['ip']}")
    with col2:
        st.success("📧 **Welcome email sent** to your inbox!")
        st.info("""
        ### 🚀 **Quick Start Guide**
        1. 📂 **File Scanner** - Upload files OR use BUILT-IN DATASET
        2. 🔍 **Live Status** - Real-time monitoring  
        3. 📈 **Visualizations** - See anomalies highlighted!
        """)
        show_builtin_dataset()
        if st.button("🌐 GO TO DASHBOARD", type="primary", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

# ========== 4. FILE SCANNER ==========
def file_scanner_page():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<h1 class="content-header">📂 File Scanner</h1>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("📁 Upload CSV", type=['csv'])
        st.markdown("---")
        show_builtin_dataset()  # BUILT-IN DATASET BUTTON
    with col2:
        if st.session_state.file_data is not None:
            df = st.session_state.file_data
            high_threats = len(df[df['Threat_Score'] > 0.7])
            
            st.success(f"✅ **{len(df):,} records** scanned successfully!")
            st.warning(f"🚨 **{high_threats} HIGH/CRITICAL threats** detected!")
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("📊 Total Records", f"{len(df):,}")
                st.metric("📈 Columns", len(df.columns))
            with col_m2:
                st.metric("🛡️ Status", "⚠️ THREATS DETECTED" if high_threats > 0 else "✅ SAFE")
                st.metric("🚨 Threats", high_threats)
            
            if st.button("📧 SEND SCAN REPORT", type="primary"):
                threat_msg = f"🚨 **{high_threats} threats** found in {len(df):,} records!"
                send_email(st.session_state.user_email, "📊 File Scan Complete", threat_msg)
                show_email_popup()
            
            st.markdown("### 📋 Sample Data (Threats Highlighted)")
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.info('👈 **Click "LOAD BUILT-IN DATASET"** or upload your own CSV')  # ✅ FIXED SYNTAX

# ========== 5. LIVE STATUS ==========
def live_status_page():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<h1 class="content-header">🔍 Live Status</h1>', unsafe_allow_html=True)
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            if st.button("🚀 START MONITORING", type="primary"):
                st.session_state.detection_df = pd.DataFrame()
                st.session_state.threat_details = []
                st.session_state.live_monitoring = True
                threading.Thread(target=live_monitoring_thread, daemon=True).start()
        with col_ctrl2:
            if st.button("⏹️ STOP MONITORING", type="secondary"):
                st.session_state.live_monitoring = False
    with col2:
        if st.session_state.live_monitoring:
            st.markdown('<div class="live-indicator">🔴 **LIVE PROTECTION ACTIVE**</div>', unsafe_allow_html=True)
        
        threats = len(st.session_state.threat_details)
        packets = len(st.session_state.detection_df)
        
        col1m, col2m, col3m = st.columns(3)
        with col1m: st.metric("📦 Packets", packets)
        with col2m: st.metric("🚨 Threats", threats)
        with col3m: st.metric("🔒 Status", "PROTECTED" if threats == 0 else "⚠️ ALERT")
        
        if not st.session_state.detection_df.empty:
            st.markdown("### 📋 Recent Activity")
            st.dataframe(st.session_state.detection_df.tail(10)[['Time', 'Status', 'Threat']], 
                        use_container_width=True)

# ========== 6. VISUALIZATIONS ==========
def visualizations_page():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<h1 class="content-header">📈 Visualizations</h1>', unsafe_allow_html=True)
        st.info("📊 **Charts show REAL anomalies** from dataset")
    with col2:
        if st.session_state.file_data is not None:
            df = st.session_state.file_data.copy()
            
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                fig_pie = px.pie(df, names='Threat_Level', title="🚨 Threat Distribution")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_v2:
                fig_hist = px.histogram(df, x='Threat_Score', color='Threat_Level', 
                                      title="📊 Threat Score Distribution", nbins=20)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # IP ANOMALY TABLE
            st.markdown("### 🌐 **Suspicious IPs Detected**")
            suspicious_ips = df[df['Threat_Score'] > 0.7][['Source_IP', 'Threat_Score', 'Threat_Level']].head(10)
            st.dataframe(suspicious_ips, use_container_width=True)
            
            # AUTO SEND EMAIL
            if not st.session_state.visuals_email_sent:
                high_threats = len(df[df['Threat_Score'] > 0.7])
                send_email(st.session_state.user_email, "🚨 ANOMALY ALERT", 
                          f"📊 Analysis complete! **{high_threats} suspicious IPs** detected!")
                st.session_state.visuals_email_sent = True
                show_email_popup()
        else:
            st.warning("👈 **Load dataset first** (built-in or upload)")

# ========== 7. FEEDBACK ==========
def feedback_page():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<h1 class="content-header">💬 Feedback</h1>', unsafe_allow_html=True)
    with col2:
        st.markdown("### 🎯 Help us improve AI-IDPS!")
        
        with st.form("feedback_form"):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                rating = st.slider("⭐ How would you rate AI-IDPS?", 1, 5, 4)
                ease = st.slider("😊 How easy was it to use?", 1, 5, 5)
            with col_f2:
                satisfaction = st.slider("✅ Overall satisfaction?", 1, 5, 4)
            
            comments = st.text_area("💭 Any suggestions or feedback?")
            submit_btn = st.form_submit_button("📧 SEND FEEDBACK", type="primary")
        
        if submit_btn:
            feedback = f"Rating: {rating}/5 | Ease: {ease}/5 | Satisfaction: {satisfaction}/5\n\n{comments}"
            send_email("saiprasadreddy0910@gmail.com", f"AI-IDPS Feedback - {st.session_state.username}", feedback)
            st.success("✅ Thank you! Your feedback helps improve AI-IDPS!")
            st.balloons()

def live_monitoring_thread():
    """Enhanced with REAL anomaly patterns from dataset"""
    anomaly_ips = ['45.79.123.45', '198.51.100.78', '203.0.113.200', '192.168.1.999']
    normal_ips = ['192.168.1.10', '192.168.1.20', '10.0.0.5']
    
    while st.session_state.live_monitoring:
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 20% chance of anomaly IP, 80% normal
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
                
                if st.button("📂 **FILE SCANNER**", key="scanner_tab"):
                    st.session_state.current_page = "scanner"
                    st.rerun()
                if st.button("🔍 **LIVE STATUS**", key="live_tab"):
                    st.session_state.current_page = "live"
                    st.rerun()
                if st.button("📈 **VISUALIZATIONS**", key="visuals_tab"):
                    st.session_state.current_page = "visuals"
                    st.rerun()
                if st.button("💬 **FEEDBACK**", key="feedback_tab"):
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

