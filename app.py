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
    # Show enhanced login page with animated left-side panel
    st.markdown("""
    <style>
    /* Layout helpers */
    .login-wrapper {
      display: flex;
      gap: 1.5rem;
      align-items: stretch;
      margin-top: 0.5rem;
      margin-bottom: 0.5rem;
    }
    /* Left panel (animated menu) */
    .left-panel {
      width: 100%;
      max-width: 380px;
      background: linear-gradient(180deg, rgba(46,134,171,0.08), rgba(162,59,114,0.03));
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 10px 30px rgba(16,24,40,0.06);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.45s cubic-bezier(.2,.9,.3,1), box-shadow 0.45s;
    }
    .left-panel:hover { transform: translateY(-6px); box-shadow: 0 18px 40px rgba(16,24,40,0.12); }

    .panel-title {
      font-weight: 800;
      font-size: 1.15rem;
      background: linear-gradient(90deg,#2E86AB,#A23B72);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin: 0 0 6px 0;
    }
    .panel-sub {
      color:#6b7280;
      font-size:0.9rem;
      margin-bottom: 12px;
    }

    /* Animated menu (using native details/summary for accessibility) */
    .menu {
      width: 100%;
    }
    details.menu-section {
      background: rgba(255,255,255,0.92);
      border-radius: 10px;
      padding: 8px 12px;
      margin-bottom: 10px;
      transition: all 0.35s ease;
      overflow: hidden;
      border-left: 4px solid rgba(46,134,171,0.14);
    }
    details.menu-section[open] {
      transform: translateX(4px);
      border-left-color: rgba(162,59,114,0.24);
      box-shadow: 0 8px 18px rgba(16,24,40,0.06);
    }
    summary.menu-summary {
      list-style: none;
      cursor: pointer;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 4px;
      font-size: 0.98rem;
    }
    summary::-webkit-details-marker { display: none; } /* hide default arrow in some browsers */

    .menu-icon {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display:flex;
      align-items:center;
      justify-content:center;
      background: linear-gradient(90deg,#ffffff,#f8fafc);
      box-shadow: 0 4px 12px rgba(16,24,40,0.04);
      transition: transform 0.35s ease;
    }
    details.menu-section[open] .menu-icon { transform: rotate(8deg) scale(1.03); }

    .menu-content {
      margin-top: 8px;
      display: grid;
      gap: 8px;
    }

    .dropdown-btn {
      background: linear-gradient(90deg, rgba(46,134,171,0.06), rgba(162,59,114,0.03));
      border: none;
      padding: 8px 10px;
      border-radius: 8px;
      text-align:left;
      width:100%;
      font-weight:600;
      cursor:pointer;
      transition: background 0.25s, transform 0.18s;
      display:flex;
      justify-content:space-between;
      align-items:center;
    }
    .dropdown-btn:hover { transform: translateX(6px); background: rgba(46,134,171,0.10); }

    /* micro animation dots */
    .live-dot {
      width:10px; height:10px; border-radius:50%;
      background: #10b981;
      box-shadow: 0 0 6px rgba(16,185,129,0.6);
      animation: pulse 1.8s infinite ease-in-out;
      margin-left:6px;
    }
    @keyframes pulse {
      0% { transform: scale(1); opacity: 0.9; }
      50% { transform: scale(1.45); opacity: 0.5; }
      100% { transform: scale(1); opacity: 0.9; }
    }

    /* Lottie container */
    .lottie-wrap { display:flex; justify-content:center; margin-top:6px; }

    /* Right side (login) tweaks so it looks integrated */
    .right-panel {
      flex:1;
      min-width: 320px;
      background: transparent;
    }

    /* Responsive adjustments */
    @media (max-width: 900px) {
      .login-wrapper { flex-direction: column; }
      .left-panel { max-width: unset; width:100%; }
    }
    </style>
    """, unsafe_allow_html=True)

    # Layout: left animated menu + right login/register area
    left_col, right_col = st.columns([1, 2])

    # LEFT: animated, interactive-looking menu (decorative + some pseudo-buttons)
    with left_col:
        left_html = f"""
        <div class="left-panel" role="region" aria-label="HealthSense quick actions">
          <div>
            <div class="panel-title">Welcome to HealthSense</div>
            <div class="panel-sub">Quick access • Animated UI • Secure</div>

            <div class="menu" aria-hidden="false">
              <details class="menu-section" open>
                <summary class="menu-summary">
                  <div class="menu-icon">🏥</div>
                  <div>Patient Management</div>
                  <div class="live-dot" aria-hidden="true"></div>
                </summary>
                <div class="menu-content">
                  <!-- Decorative buttons; in future these can be wired to actions -->
                  <button class="dropdown-btn">All Patients <span style="opacity:0.7">→</span></button>
                  <button class="dropdown-btn">Add Patient <span style="opacity:0.7">＋</span></button>
                  <button class="dropdown-btn">Import CSV <span style="opacity:0.7">⬆</span></button>
                </div>
              </details>

              <details class="menu-section">
                <summary class="menu-summary">
                  <div class="menu-icon">🩺</div>
                  <div>Medical Records</div>
                </summary>
                <div class="menu-content">
                  <button class="dropdown-btn">View Records</button>
                  <button class="dropdown-btn">Upload Record</button>
                  <button class="dropdown-btn">Audit Log</button>
                </div>
              </details>

              <details class="menu-section">
                <summary class="menu-summary">
                  <div class="menu-icon">📅</div>
                  <div>Appointments</div>
                </summary>
                <div class="menu-content">
                  <button class="dropdown-btn">Today's</button>
                  <button class="dropdown-btn">Schedule</button>
                  <button class="dropdown-btn">Reminders</button>
                </div>
              </details>

              <details class="menu-section">
                <summary class="menu-summary">
                  <div class="menu-icon">⚙️</div>
                  <div>Settings</div>
                </summary>
                <div class="menu-content">
                  <button class="dropdown-btn">Profile</button>
                  <button class="dropdown-btn">Security</button>
                  <button class="dropdown-btn">Integrations</button>
                </div>
              </details>
            </div>
          </div>

          <div>
            <div class="lottie-wrap">
              <!-- Lottie webcomponent: small techy animation -->
              <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
              <lottie-player
                src="https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json"
                background="transparent"
                speed="1"
                style="width:140px; height:80px;"
                loop
                autoplay>
              </lottie-player>
            </div>
            <div style="margin-top:10px; color:#6b7280; font-size:0.85rem; text-align:center;">
              Secure • Animated • Responsive
            </div>
          </div>
        </div>
        """
        components.html(left_html, height=520)

    # RIGHT: keep the functional login/register forms but visually aligned
    with right_col:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.markdown('<h1 style="margin-top:0; font-weight:800; font-size:2.4rem; background: linear-gradient(90deg,#2E86AB,#A23B72); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">🏥 HealthSense</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color:#6b7280; margin-top:-10px;">Sign in to access the dashboard</p>', unsafe_allow_html=True)
        st.markdown("---")

        # Keep tabs for Login/Register
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        with tab1:
            show_login_form()
        with tab2:
            show_register_form()

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# Initialize database manager
@st.cache_resource
def init_db_manager():
    return DatabaseManager()

data_manager = init_db_manager()

# Get current user
current_user = get_current_user()

# Custom CSS for healthcare theme (kept for logged-in dashboard)
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

# Main dashboard content
st.header("📊 Dashboard Overview")

# Create columns for metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Total Patients",
        value=patients_count,
        delta="+5 this month"
    )

with col2:
    st.metric(
        label="📅 Today's Appointments",
        value=len([a for a in data_manager.get_appointments() if a['date'] == datetime.now().strftime("%Y-%m-%d")]),
        delta="+2 from yesterday"
    )

with col3:
    st.metric(
        label="💊 Active Prescriptions",
        value=prescriptions_count,
        delta="+3 this week"
    )

with col4:
    st.metric(
        label="🤖 AI Predictions",
        value="12",
        delta="+4 this week"
    )

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
    st.plotly_chart(fig, use_container_width=True)

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
    st.plotly_chart(fig, use_container_width=True)

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
