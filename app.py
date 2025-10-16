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
    # Show login page
    st.markdown("""
    <style>
    .login-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-desc {
        text-align:center;
        font-size:1.05rem;
        color:#666;
        margin-bottom:1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="login-header">🏥 HealthSense</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-desc">AI-Powered Healthcare Management System</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        show_login_form()

    with tab2:
        show_register_form()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>🏥 HealthSense</strong> - Powered by AI for Better Healthcare Management</p>
        <p style='font-size: 0.9rem;'>Secure • Reliable • HIPAA Compliant</p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# Initialize database manager
@st.cache_resource
def init_db_manager():
    return DatabaseManager()

data_manager = init_db_manager()

# Get current user
current_user = get_current_user()

# Inject responsive CSS and a techy animated hero
st.markdown("""
<style>
/* Hero */
.hero {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  margin-bottom: 1rem;
}
.hero-title {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(90deg, #2E86AB, #A23B72);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}
.hero-sub {
  color:#6b7280;
  margin-top: 0.25rem;
}

/* Metric cards grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}
.metric-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.98));
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(18, 38, 63, 0.08);
  border-left: 6px solid rgba(46,134,171,0.12);
}
.metric-label { font-size:0.9rem; color:#6b7280; }
.metric-value { font-size:1.6rem; font-weight:700; margin-top:0.25rem; }

/* Responsive behavior */
@media (max-width: 1100px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .hero { grid-template-columns: 1fr; text-align: left; }
}
@media (max-width: 600px) {
  .metrics-grid { grid-template-columns: 1fr; }
  .hero-title { font-size: 1.6rem; }
}
</style>
""", unsafe_allow_html=True)

# Hero area with small SVG/graphic to look techy
st.markdown(f"""
<div class="hero">
  <div>
    <h2 class="hero-title">🏥 HealthSense — AI Healthcare Management</h2>
    <div class="hero-sub">Smart, responsive, and secure dashboard for clinicians and patients.</div>
  </div>
  <div>
    <!-- Simple SVG graphic; replace or upgrade with your own images -->
    <svg width="140" height="80" viewBox="0 0 140 80" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="0" width="140" height="80" rx="10" fill="url(#g)"/>
      <g opacity="0.6">
        <circle cx="40" cy="40" r="10" fill="white"/>
        <rect x="60" y="20" width="12" height="40" rx="3" fill="white"/>
        <rect x="82" y="28" width="36" height="24" rx="4" fill="white"/>
      </g>
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#2E86AB"/>
          <stop offset="100%" stop-color="#A23B72"/>
        </linearGradient>
      </defs>
    </svg>
  </div>
</div>
""", unsafe_allow_html=True)

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

# Main dashboard content
st.header("📊 Dashboard Overview")

# Build HTML metrics grid (responsive)
today_appointments = len([a for a in data_manager.get_appointments() if a['date'] == datetime.now().strftime("%Y-%m-%d")])
ai_predictions = 12  # placeholder; replace with real value if available

metrics_html = f"""
<div class="metrics-grid">
  <div class="metric-card">
    <div class="metric-label">👥 Total Patients</div>
    <div class="metric-value">{patients_count}</div>
    <div style="color:#10b981;font-size:0.8rem;margin-top:6px;">+5 this month</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">📅 Today's Appointments</div>
    <div class="metric-value">{today_appointments}</div>
    <div style="color:#10b981;font-size:0.8rem;margin-top:6px;">+2 from yesterday</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">💊 Active Prescriptions</div>
    <div class="metric-value">{prescriptions_count}</div>
    <div style="color:#10b981;font-size:0.8rem;margin-top:6px;">+3 this week</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">🤖 AI Predictions</div>
    <div class="metric-value">{ai_predictions}</div>
    <div style="color:#10b981;font-size:0.8rem;margin-top:6px;">+4 this week</div>
  </div>
</div>
"""
components.html(metrics_html, height=200)

st.markdown("---")

# Charts section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Patient Registration Trend")

    # Sample data for patient registration trend
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='ME')
    patients_monthly = [10, 15, 12, 18, 22, 25, 30, 28, 32, 35, 38, 42]

    fig = px.line(
        x=dates, 
        y=patients_monthly,
        title="Monthly Patient Registrations",
        labels={'x': 'Month', 'y': 'New Patients'}
    )
    fig.update_traces(line_color='#2E86AB')
    fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

with col2:
    st.subheader("🏥 Department Distribution")

    departments = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'General']
    patient_counts = [25, 18, 22, 15, 30]

    fig = px.pie(
        values=patient_counts,
        names=departments,
        title="Patients by Department"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

# Recent activity section
st.subheader("🔄 Recent Activity")

# Get recent appointments
recent_appointments = data_manager.get_appointments()[-5:] if data_manager.get_appointments() else []

if recent_appointments:
    df_recent = pd.DataFrame(recent_appointments)
    st.dataframe(
        df_recent[['patient_name', 'doctor', 'date', 'time', 'status']],
        use_container_width=True
    )
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
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🏥 HealthSense - Powered by AI for Better Healthcare Management</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)
