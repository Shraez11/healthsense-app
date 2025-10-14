import streamlit as st
from utils.auth import init_auth, is_authenticated, show_login_form, show_register_form, logout, get_current_user

# Page configuration
st.set_page_config(
    page_title="HealthSense - Login",
    page_icon="🔐",
    layout="centered"
)

# Initialize authentication
init_auth()

# Custom CSS
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
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="login-header">🏥 HealthSense</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Healthcare Management System</p>', unsafe_allow_html=True)

st.markdown("---")

# Check if already authenticated
if is_authenticated():
    user = get_current_user()
    st.success(f"✅ Welcome back, {user['full_name']}!")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.metric("Role", user['role'].title())
    
    with col2:
        st.metric("Username", user['username'])
    
    with col3:
        if st.button("Logout", type="secondary"):
            logout()
            st.rerun()
    
    st.markdown("---")
    st.info("👉 Use the sidebar navigation to access the healthcare management features.")
    
else:
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
