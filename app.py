import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.db_manager import DatabaseManager
from utils.auth import init_auth, require_auth, is_authenticated, get_current_user, logout, show_login_form, show_register_form
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="HealthSense - AI Healthcare Management",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication and database
init_auth()

# Require authentication
if not is_authenticated():
    # Classy decorative left panel + original login/register on the right
    st.markdown("""
    <style>
    /* Layout */
    .login-row { display:flex; gap: 1.5rem; align-items:flex-start; margin-top:14px; margin-bottom:8px; }
    @media (max-width:900px) { .login-row { flex-direction:column; } }

    /* Left decorative glass card */
    .left-glass {
      width:100%;
      max-width:360px;
      padding:22px;
      border-radius:16px;
      background: linear-gradient(180deg, rgba(255,255,255,0.66), rgba(250,250,252,0.54));
      backdrop-filter: blur(6px) saturate(120%);
      -webkit-backdrop-filter: blur(6px) saturate(120%);
      border: 1px solid rgba(255,255,255,0.5);
      box-shadow: 0 18px 40px rgba(8,12,25,0.06);
      position:relative;
      overflow:hidden;
    }

    /* Floating decorative blobs */
    .blob {
      position:absolute;
      border-radius:50%;
      filter: blur(18px);
      opacity:0.95;
      animation: floaty 7s ease-in-out infinite;
      transform-origin: center;
      mix-blend-mode: screen;
    }
    .blob.a{ width:160px; height:160px; background: rgba(46,134,171,0.15); right:-40px; top:-50px; animation-duration:8s; }
    .blob.b{ width:100px; height:100px; background: rgba(162,59,114,0.10); left:-30px; bottom:-30px; animation-duration:5.8s; }
    .blob.c{ width:70px; height:70px; background: rgba(46,134,171,0.08); left:18%; top:45%; animation-duration:9s; }

    @keyframes floaty {
      0% { transform: translateY(0) scale(1); }
      50% { transform: translateY(-14px) scale(1.03) rotate(4deg); }
      100% { transform: translateY(0) scale(1); }
    }

    /* Content inside glass */
    .left-title { font-weight:800; font-size:1.08rem; margin-bottom:6px; background: linear-gradient(90deg,#2E86AB,#A23B72); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .left-sub { color:#6b7280; font-size:0.92rem; margin-bottom:12px; }

    .features { display:grid; grid-template-columns:1fr; gap:8px; margin-top:6px; }
    .feature {
      display:flex; justify-content:space-between; align-items:center;
      background: rgba(255,255,255,0.9); padding:10px 12px; border-radius:10px;
      box-shadow: 0 8px 22px rgba(10,14,24,0.04); border-left: 4px solid rgba(46,134,171,0.10);
      transition: transform 0.18s ease, box-shadow 0.18s ease;
      cursor:default;
    }
    .feature:hover { transform: translateY(-6px); box-shadow: 0 18px 40px rgba(10,14,24,0.06); }
    .feature .label { font-weight:700; color:#0f172a; }
    .feature .meta { font-size:0.82rem; color:#6b7280; }

    /* CTA */
    .cta { margin-top:14px; display:flex; justify-content:center; }
    .cta-btn {
      background: linear-gradient(90deg,#2E86AB,#A23B72);
      color:white; padding:10px 16px; border-radius:12px; border:none; font-weight:800; cursor:pointer;
      box-shadow: 0 12px 30px rgba(46,134,171,0.12); transition: transform 0.18s ease, box-shadow 0.18s;
    }
    .cta-btn:hover { transform: translateY(-6px); box-shadow: 0 20px 44px rgba(46,134,171,0.16); }

    /* small lottie area */
    .lottie-wrap { display:flex; justify-content:center; margin-top:12px; }

    /* Right panel */
    .right-panel { flex:1; min-width:320px; }

    </style>
    """, unsafe_allow_html=True)

    # Two-column layout: left decorative, right functional
    col_left, col_right = st.columns([1, 2])

    with col_left:
        left_html = """
        <div class="left-glass" role="complementary" aria-label="HealthSense preview">
          <div class="blob a" aria-hidden="true"></div>
          <div class="blob b" aria-hidden="true"></div>
          <div class="blob c" aria-hidden="true"></div>

          <div style="position:relative; z-index:2;">
            <div class="left-title">Welcome to HealthSense</div>
            <div class="left-sub">Modern AI-powered healthcare — secure, fast, insightful.</div>

            <div class="features" aria-hidden="false">
              <div class="feature"><div class="label">Secure Records</div><div class="meta">End-to-end encrypted</div></div>
              <div class="feature"><div class="label">Smart Scheduling</div><div class="meta">AI-assisted</div></div>
              <div class="feature"><div class="label">Predictive Insights</div><div class="meta">Model-driven</div></div>
            </div>

            <div class="lottie-wrap" aria-hidden="true">
              <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
              <lottie-player
                src="https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json"
                background="transparent"
                speed="1"
                style="width:160px; height:92px;"
                loop
                autoplay>
              </lottie-player>
            </div>

            <div class="cta">
              <button class="cta-btn" onclick="/* decorative only */">Explore Features</button>
            </div>
          </div>
        </div>
        """
        # components.html used to keep the precise layout and animations intact
        components.html(left_html, height=440)

    with col_right:
        # Keep the login/register layout and logic unchanged
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.markdown('<h1 style="margin-top:0; font-weight:800; font-size:2.4rem; background: linear-gradient(90deg,#2E86AB,#A23B72); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">🏥 HealthSense</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color:#6b7280; margin-top:-10px;">Sign in to access the dashboard</p>', unsafe_allow_html=True)
        st.markdown("---")

        # Original login/register tabs
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        with tab1:
            show_login_form()
        with tab2:
            show_register_form()

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# Initialize database manager
@st.cache_resource
def init_db_manager():
    return DatabaseManager()

data_manager = init_db_manager()

# Get current user
current_user = get_current_user()

# Custom CSS for healthcare theme (main app)
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 1rem 0;
    background: linear-gradient(90deg, #2E86AB, #A23B72);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #2E86AB;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🏥 HealthSense - AI Healthcare Management System</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")

# User info in sidebar
st.sidebar.markdown("---")
st.sidebar.write(f"👤 **{current_user['full_name']}**")
st.sidebar.write(f"🏷️ Role: {current_user['role'].title()}")

if st.sidebar.button("🚪 Logout", type="secondary"):
    logout()
    st.rerun()

st.sidebar.markdown("---")

# Quick stats in sidebar
patients_count = len(data_manager.get_patients())
appointments_count = len(data_manager.get_appointments())
prescriptions_count = len(data_manager.get_prescriptions())

st.sidebar.metric("Total Patients", patients_count)
st.sidebar.metric("Total Appointments", appointments_count)
st.sidebar.metric("Active Prescriptions", prescriptions_count)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Quick Tip:** Use the navigation pages above to access different modules of the healthcare system.")

# Main dashboard content (keeps your original layout)
st.header("📊 Dashboard Overview")

# Build HTML metrics grid (fallback to simple columns)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="👥 Total Patients", value=patients_count, delta="+5 this month")
with col2:
    st.metric(label="📅 Today's Appointments", value=len([a for a in data_manager.get_appointments() if a['date'] == datetime.now().strftime("%Y-%m-%d")]), delta="+2 from yesterday")
with col3:
    st.metric(label="💊 Active Prescriptions", value=prescriptions_count, delta="+3 this week")
with col4:
    st.metric(label="🤖 AI Predictions", value="12", delta="+4 this week")

st.markdown("---")

# Charts section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Patient Registration Trend")
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='ME')
    patients_monthly = [10, 15, 12, 18, 22, 25, 30, 28, 32, 35, 38, 42]
    fig = px.line(x=dates, y=patients_monthly, title="Monthly Patient Registrations", labels={'x':'Month','y':'New Patients'})
    fig.update_traces(line_color='#2E86AB')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏥 Department Distribution")
    departments = ['Cardiology','Neurology','Orthopedics','Pediatrics','General']
    patient_counts = [25,18,22,15,30]
    fig = px.pie(values=patient_counts, names=departments, title="Patients by Department")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

# Recent activity
st.subheader("🔄 Recent Activity")
recent_appointments = data_manager.get_appointments()[-5:] if data_manager.get_appointments() else []
if recent_appointments:
    df_recent = pd.DataFrame(recent_appointments)
    st.dataframe(df_recent[['patient_name','doctor','date','time','status']], use_container_width=True)
else:
    st.info("No recent appointments to display.")

# System status
st.markdown("---")
st.subheader("🔧 System Status")
col1, col2, col3 = st.columns(3)
with col1:
    st.success("✅ Database: Online")
with col2:
    st.success("✅ AI Services: Active")
with col3:
    st.success("✅ Backup: Updated")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏥 HealthSense - Powered by AI for Better Healthcare Management</p>
    <p>Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
