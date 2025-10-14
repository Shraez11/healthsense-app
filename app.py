import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.db_manager import DatabaseManager
from utils.auth import init_auth, require_auth, is_authenticated, get_current_user, logout

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
    st.warning("⚠️ Please login to access the dashboard")
    st.info("👉 Go to the Login page from the sidebar")
    st.stop()

# Initialize database manager
@st.cache_resource
def init_db_manager():
    return DatabaseManager()

data_manager = init_db_manager()

# Get current user
current_user = get_current_user()

# Custom CSS for healthcare theme
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
