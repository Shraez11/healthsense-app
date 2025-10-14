import streamlit as st
import bcrypt
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from utils.database import Base, SessionLocal, engine

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'doctor', 'patient'
    is_active = Column(Boolean, default=True)
    created_at = Column(String)

# Create user table
Base.metadata.create_all(bind=engine)

def hash_password(password):
    """Hash a password for secure storage using bcrypt with salt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash (supports both legacy SHA-256 and bcrypt)"""
    # Check if it's a bcrypt hash (starts with $2b$ or $2a$)
    if password_hash.startswith(('$2b$', '$2a$')):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False
    else:
        # Legacy SHA-256 hash - verify and upgrade
        import hashlib
        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        return legacy_hash == password_hash

def create_user(username, email, password, full_name, role='patient'):
    """Create a new user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return None, "Username or email already exists"
        
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True,
            created_at=datetime.now().isoformat()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user, None
    except Exception as e:
        db.rollback()
        return None, str(e)
    finally:
        db.close()

def authenticate_user(username, password):
    """Authenticate a user and upgrade legacy password hashes"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if user and user.is_active and verify_password(password, user.password_hash):
            # Upgrade legacy SHA-256 hash to bcrypt on successful login
            if not user.password_hash.startswith(('$2b$', '$2a$')):
                user.password_hash = hash_password(password)
                db.commit()
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            }
        return None
    finally:
        db.close()

def get_all_users():
    """Get all users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'full_name': u.full_name,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at
        } for u in users]
    finally:
        db.close()

def create_default_users():
    """Create default users if they don't exist"""
    # Create admin user
    create_user('admin', 'admin@healthsense.com', 'admin123', 'System Administrator', 'admin')
    
    # Create sample doctor
    create_user('dr_smith', 'dr.smith@healthsense.com', 'doctor123', 'Dr. John Smith', 'doctor')
    
    # Create sample patient
    create_user('patient1', 'patient@healthsense.com', 'patient123', 'John Doe', 'patient')

def init_auth():
    """Initialize authentication system"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
    
    # Create default users on first run
    if 'auth_initialized' not in st.session_state:
        create_default_users()
        st.session_state.auth_initialized = True

def login(username, password):
    """Login user"""
    user = authenticate_user(username, password)
    if user:
        st.session_state.authenticated = True
        st.session_state.user = user
        return True
    return False

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def get_current_user():
    """Get current authenticated user"""
    return st.session_state.get('user', None)

def has_role(role):
    """Check if current user has specified role"""
    user = get_current_user()
    if user:
        return user['role'] == role
    return False

def is_admin():
    """Check if current user is admin"""
    return has_role('admin')

def is_doctor():
    """Check if current user is doctor"""
    return has_role('doctor')

def is_patient():
    """Check if current user is patient"""
    return has_role('patient')

def require_auth(allowed_roles=None):
    """Decorator to require authentication for a page"""
    if not is_authenticated():
        st.warning("⚠️ Please login to access this page")
        show_login_form()
        st.stop()
    
    if allowed_roles:
        user = get_current_user()
        if user['role'] not in allowed_roles:
            st.error("❌ You don't have permission to access this page")
            st.stop()

def show_login_form():
    """Display login form"""
    st.subheader("🔐 Login to HealthSense")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", type="primary")
        
        if submit:
            if login(username, password):
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    with st.expander("ℹ️ Demo Credentials"):
        st.write("**Admin:** username: `admin`, password: `admin123`")
        st.write("**Doctor:** username: `dr_smith`, password: `doctor123`")
        st.write("**Patient:** username: `patient1`, password: `patient123`")

def show_register_form():
    """Display registration form"""
    st.subheader("📝 Register New Account")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*")
            email = st.text_input("Email*")
            password = st.text_input("Password*", type="password")
        
        with col2:
            full_name = st.text_input("Full Name*")
            role = st.selectbox("Role*", ["patient", "doctor"])
            confirm_password = st.text_input("Confirm Password*", type="password")
        
        submit = st.form_submit_button("Register", type="primary")
        
        if submit:
            if not all([username, email, password, full_name]):
                st.error("Please fill in all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                user, error = create_user(username, email, password, full_name, role)
                if user:
                    st.success("✅ Registration successful! You can now login.")
                else:
                    st.error(f"❌ Registration failed: {error}")
