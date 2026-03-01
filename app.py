import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
from datetime import datetime
import smtplib
from email.message import EmailMessage
import random
import re

# --- 1. Page Config ---
st.set_page_config(page_title="VANTAGE-AI Dashboard", layout="wide")

# Initialize Session States
if 'user_db' not in st.session_state: st.session_state.user_db = {"admin": "admin123"}
if 'signup_mode' not in st.session_state: st.session_state.signup_mode = False
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame([{"Day": "Day 1", "Topic": "Technical Analysis Live", "Time": "7:00 PM"}])
if 'daily_data' not in st.session_state: st.session_state.daily_data = None
if 'weekly_data' not in st.session_state: st.session_state.weekly_data = None
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'user_id' not in st.session_state: st.session_state.user_id = "admin"
if 'theme' not in st.session_state: st.session_state.theme = "Dark Mode"

# --- THEME LOGIC ---
# --- THEME LOGIC (Replace Line 30-52 with this) ---
if 'report_theme' in st.session_state:
    st.session_state.theme = st.session_state.report_theme

if st.session_state.theme == "Light Mode":
    bg_color = "#FFFFFF"      # Pure White Background
    text_color = "#121212"    # Dark Text for readability
    sidebar_bg = "#F8F9FB"    # Subtle Grey Sidebar
    accent_color = "#007BFF"  # Blue accent
else:
    bg_color = "#0E1117"      # Dark Navy/Black
    text_color = "#FFFFFF"    # White Text
    sidebar_bg = "#161B22"    # Darker Sidebar
    accent_color = "#00CC96"  # Teal accent

st.markdown(f"""
    <style>
    /* Main App Background and Text */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid #ddd;
    }}
    /* Titles and Headers */
    h1, h2, h3, p, span, label, .stMarkdown {{
        color: {text_color} !important;
    }}
    /* Input Box styling for Light Mode visibility */
    .stTextInput>div>div>input, .stSelectbox>div {{
        background-color: {"#f9f9f9" if st.session_state.theme == "Light Mode" else "#262730"};
        color: {text_color};
    }}
    /* Tab styling */
    button[data-baseweb="tab"] {{
        color: {text_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)
# --- 2. Login ---
# --- 2. Login & Registration ---
if not st.session_state.authenticated:
    _, col, _ = st.columns([1, 0.8, 1])
    with col:
        if not st.session_state.signup_mode:
            st.title("VANTAGE-AI Login")
            method = st.radio("Method", ["Password", "Email OTP"], horizontal=True)
            
            if method == "Password":
                user = st.text_input("Creator ID")
                pw = st.text_input("Access Key", type="password")
                if st.button("Access Agent", use_container_width=True):
                    if user in st.session_state.user_db and st.session_state.user_db[user] == pw:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user
                        st.rerun()
                    else: st.error("Invalid Credentials")
            else:
                email = st.text_input("Email Address")
                if st.button("Send OTP"):
                    st.session_state.otp = "1234" # Dummy for testing, use send_otp(email) for real
                    st.success("OTP sent to email!")
                entered_otp = st.text_input("Enter OTP")
                if st.button("Verify"):
                    if entered_otp == st.session_state.get('otp'):
                        st.session_state.authenticated = True
                        st.session_state.user_id = email
                        st.rerun()

            if st.button("New User? Register here"):
                st.session_state.signup_mode = True
                st.rerun()
        else:
            st.title("New Registration")
            new_id = st.text_input("New Creator ID")
            new_pw = st.text_input("Set Access Key", type="password")
            if st.button("Create Account"):
                st.session_state.user_db[new_id] = new_pw
                st.success("Account Created!")
                st.session_state.signup_mode = False
                st.rerun()
            if st.button("Back to Login"):
                st.session_state.signup_mode = False
                st.rerun()
    st.stop()
# Email Setup
def send_otp(receiver_email):
    otp = str(random.randint(1000, 9999))
    # Note: Use Google App Password here
    try:
        msg = EmailMessage()
        msg.set_content(f"Your VANTAGE-AI Login OTP is: {otp}")
        msg['Subject'] = 'VANTAGE-AI Access Code'
        msg['From'] = "your-email@gmail.com"
        msg['To'] = receiver_email
        # server = smtplib.SMTP_SSL('smtp.gmail.com', 465) # Inidially commented for safety
        # server.login("your-email@gmail.com", "your-app-password")
        # server.send_message(msg)
        # server.quit()
        return otp
    except: return None

# FIXED PDF GENERATOR (Fixes UnicodeEncodeError)
def generate_pdf(title, strategy="", extras=[], chart_type="daily"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    # Remove non-latin characters manually to avoid crash
    clean_title = re.sub(r'[^\x00-\x7F]+', '', title)
    pdf.cell(200, 10, clean_title, ln=True, align='C')
    pdf.ln(10)
    
    plt.figure(figsize=(5,3))
    if chart_type == "daily":
        plt.bar(["Positive", "Negative"], [80, 20], color=['#87CEFA', '#1E90FF'])
    else:
        plt.plot(["Mon", "Tue", "Wed", "Thu", "Fri"], [60, 70, 85, 75, 90], marker='o', color='#87CEFA')
    
    img_path = f"temp_{chart_type}.png"
    plt.savefig(img_path)
    plt.close()
    pdf.image(img_path, x=50, w=110)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)

    clean_strategy = re.sub(r'[^\x00-\x7F]+', '', strategy)
    pdf.multi_cell(0, 10, f"Strategy: {clean_strategy}")
    
    for item in extras:
        clean_item = re.sub(r'[^\x00-\x7F]+', '', item)
        pdf.multi_cell(0, 10, f"- {clean_item}")
        
    pdf_output = pdf.output(dest='S').encode('latin-1')
    if os.path.exists(img_path): os.remove(img_path)
    return pdf_output

# --- 3. Sidebar ---
st.sidebar.title("VANTAGE-AI")
page = st.sidebar.radio("Navigate to:", ["Analysis Dashboard", "Content Calendar", "Settings"])

if page == "Analysis Dashboard":
    tab1, tab2 = st.tabs(["Daily Analysis Report", "Weekly Strategic Overview"])

    with tab1:
        st.header("Daily Analysis Report")
        platform = st.selectbox("Platform", ["YouTube", "Instagram", "Twitter/X", "LinkedIn"], key="d_plat")
        post_url = st.text_input(f"Enter {platform} URL:", key="d_url")
        
        if st.button("Execute Daily Analysis", use_container_width=True):
            if post_url:
                st.session_state.daily_data = {
                    "score": 80, 
                    "strategy": "Increasing focus on trending topics will boost reach by 20%.",
                    "faqs": ["How to access premium content?", "Is there a community group?", "When is the next workshop?"]
                }
                new_entry = pd.DataFrame([{"Day": f"Day {len(st.session_state.history)+1}", "Topic": f"{platform} Analysis", "Time": datetime.now().strftime("%H:%M %p")}])
                st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True)
            else: st.warning("Enter URL")

        if st.session_state.daily_data:
            d = st.session_state.daily_data
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Viral Probability")
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=80, gauge={'bar': {'color': "#00cc96"}})), use_container_width=True)
            with c2:
                st.subheader("Sentiment Summary (Pie Chart)")
                st.plotly_chart(px.pie(values=[80, 20], names=["Positive", "Negative"], hole=0.4), use_container_width=True)
            
            c3, c4 = st.columns(2)
            with c3:
                st.subheader("Viewer Interaction (Bar Chart)")
                st.plotly_chart(px.bar(x=["Likes", "Comments", "Shares"], y=[500, 120, 45]), use_container_width=True)
            with c4:
                st.subheader("Viewer Expectations (FAQ)")
                for faq in d['faqs']: st.write(f"Confirmed: {faq}")
            
            st.info(f"**Growth Strategy:** {d['strategy']}")
            st.download_button("Download Daily PDF", generate_pdf("VANTAGE-AI DAILY REPORT", d['strategy'], d['faqs'], "daily"), "daily_vantage.pdf")

    with tab2:
        st.header("Weekly Strategic Overview")
        if st.button("Execute Weekly Analysis", use_container_width=True):
            st.session_state.weekly_data = {
                "score": 75,
                "suggestions": ["Suggestion 1: Create a 10-minute deep dive.", "Suggestion 2: Post 3 short-form clips.", "Suggestion 3: Conduct a Live Q&A."]
            }

        if st.session_state.weekly_data:
            w = st.session_state.weekly_data
            st.divider()
            wc1, wc2 = st.columns(2)
            with wc1:
                st.subheader("Weekly Viral Prob.")
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=75, gauge={'bar': {'color': "#87CEFA"}})), use_container_width=True)
            with wc2:
                st.subheader("Weekly Growth (Pie Chart)")
                st.plotly_chart(px.pie(values=[60, 25, 15], names=["New Subs", "Returning", "Others"]), use_container_width=True)
            
            wc3, wc4 = st.columns(2)
            with wc3:
                st.subheader("Weekly Trend (Bar Chart)")
                st.plotly_chart(px.bar(x=["Mon", "Tue", "Wed", "Thu", "Fri"], y=[60, 70, 85, 75, 90]), use_container_width=True)
            with wc4:
                st.subheader("Next Week Content Suggestions")
                for sug in w['suggestions']: st.success(sug)
            
            st.download_button(
                label="Download Weekly PDF",
                data=generate_pdf(
                    title="VANTAGE-AI WEEKLY STRATEGIC REPORT", 
                    strategy="Current analysis shows a strong growth trend.", 
                    extras=w['suggestions'], 
                    chart_type="weekly"
                ),
                file_name="weekly_vantage_report.pdf",
                mime="application/pdf"
            )

elif page == "Content Calendar":
    st.header("VANTAGE-AI Content Calendar")
    st.table(st.session_state.history)

elif page == "Settings":
    st.header("⚙️ VANTAGE-AI Settings")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Profile Information")
        st.write(f"**VANTAGE ID:** {st.session_state.user_id}")
        st.write("**Plan:** Professional Creator")
    with col2:
        st.subheader("Dashboard Preferences")
        st.checkbox("Enable Real-time Notifications", value=True)
        # Theme Selectbox connected to Session State
        st.selectbox("Report Theme", ["Dark Mode", "Light Mode"], index=0 if st.session_state.theme == "Dark Mode" else 1, key="report_theme")
        
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

st.sidebar.caption("VANTAGE-AI SaaS | v2.0 | 2026")
