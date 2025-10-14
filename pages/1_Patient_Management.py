import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db_manager import DatabaseManager
from utils.auth import init_auth, require_auth, is_authenticated

# Initialize database manager
@st.cache_resource
def get_data_manager():
    return DatabaseManager()

data_manager = get_data_manager()

st.set_page_config(page_title="Patient Management - HealthSense", page_icon="👥", layout="wide")

# Initialize authentication
init_auth()
require_auth()

st.title("👥 Patient Management System")
st.markdown("---")

# Sidebar for operations
st.sidebar.header("Patient Operations")
operation = st.sidebar.selectbox(
    "Select Operation",
    ["View All Patients", "Add New Patient", "Edit Patient", "Search Patients"]
)

if operation == "View All Patients":
    st.header("📋 All Patients")
    
    patients = data_manager.get_patients()
    
    if patients:
        # Convert to DataFrame for display
        df = pd.DataFrame(patients)
        
        # Display patients in a table
        st.dataframe(
            df[['name', 'email', 'phone', 'date_of_birth', 'gender', 'blood_group']],
            use_container_width=True
        )
        
        # Patient statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Patients", len(patients))
        
        with col2:
            male_count = len([p for p in patients if p.get('gender', '').lower() == 'male'])
            st.metric("Male Patients", male_count)
        
        with col3:
            female_count = len([p for p in patients if p.get('gender', '').lower() == 'female'])
            st.metric("Female Patients", female_count)
        
        # Delete patient option
        st.subheader("🗑️ Delete Patient")
        patient_to_delete = st.selectbox(
            "Select patient to delete",
            options=[p['id'] for p in patients],
            format_func=lambda x: next(p['name'] for p in patients if p['id'] == x),
            key="delete_patient_select"
        )
        
        if st.button("Delete Selected Patient", type="primary"):
            if st.session_state.get('confirm_delete', False):
                data_manager.delete_patient(patient_to_delete)
                st.success("Patient deleted successfully!")
                st.rerun()
            else:
                st.session_state.confirm_delete = True
                st.warning("Click again to confirm deletion")
    else:
        st.info("No patients registered yet. Add your first patient!")

elif operation == "Add New Patient":
    st.header("➕ Add New Patient")
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email Address *", placeholder="john.doe@email.com")
            phone = st.text_input("Phone Number *", placeholder="+1 234 567 8900")
            date_of_birth = st.date_input("Date of Birth *")
            
        with col2:
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
            blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
            emergency_contact = st.text_input("Emergency Contact", placeholder="+1 234 567 8901")
            address = st.text_area("Address", placeholder="123 Main St, City, State, ZIP")
        
        col3, col4 = st.columns(2)
        with col3:
            medical_history = st.text_area("Medical History", placeholder="Any chronic conditions, allergies, etc.")
        
        with col4:
            current_medications = st.text_area("Current Medications", placeholder="List current medications")
        
        insurance_info = st.text_input("Insurance Information", placeholder="Insurance provider and policy number")
        
        submitted = st.form_submit_button("Add Patient", type="primary")
        
        if submitted:
            if not all([name, email, phone, date_of_birth, gender]):
                st.error("Please fill in all required fields marked with *")
            else:
                patient_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'date_of_birth': date_of_birth.isoformat(),
                    'gender': gender,
                    'blood_group': blood_group,
                    'emergency_contact': emergency_contact,
                    'address': address,
                    'medical_history': medical_history,
                    'current_medications': current_medications,
                    'insurance_info': insurance_info,
                    'age': (datetime.now().date() - date_of_birth).days // 365
                }
                
                patient_id = data_manager.add_patient(patient_data)
                st.success(f"Patient {name} added successfully! ID: {patient_id}")
                st.balloons()

elif operation == "Edit Patient":
    st.header("✏️ Edit Patient Information")
    
    patients = data_manager.get_patients()
    
    if patients:
        selected_patient = st.selectbox(
            "Select Patient to Edit",
            options=[p['id'] for p in patients],
            format_func=lambda x: next(p['name'] for p in patients if p['id'] == x)
        )
        
        patient = data_manager.get_patient_by_id(selected_patient)
        
        if patient:
            with st.form("edit_patient_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name", value=patient.get('name', ''))
                    email = st.text_input("Email Address", value=patient.get('email', ''))
                    phone = st.text_input("Phone Number", value=patient.get('phone', ''))
                    date_of_birth = st.date_input("Date of Birth", value=datetime.fromisoformat(patient.get('date_of_birth', datetime.now().isoformat())).date())
                    
                with col2:
                    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(patient.get('gender', 'Male')))
                    blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"], 
                                             index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"].index(patient.get('blood_group', 'Unknown')))
                    emergency_contact = st.text_input("Emergency Contact", value=patient.get('emergency_contact', ''))
                    address = st.text_area("Address", value=patient.get('address', ''))
                
                col3, col4 = st.columns(2)
                with col3:
                    medical_history = st.text_area("Medical History", value=patient.get('medical_history', ''))
                
                with col4:
                    current_medications = st.text_area("Current Medications", value=patient.get('current_medications', ''))
                
                insurance_info = st.text_input("Insurance Information", value=patient.get('insurance_info', ''))
                
                submitted = st.form_submit_button("Update Patient", type="primary")
                
                if submitted:
                    updated_data = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'date_of_birth': date_of_birth.isoformat(),
                        'gender': gender,
                        'blood_group': blood_group,
                        'emergency_contact': emergency_contact,
                        'address': address,
                        'medical_history': medical_history,
                        'current_medications': current_medications,
                        'insurance_info': insurance_info,
                        'age': (datetime.now().date() - date_of_birth).days // 365
                    }
                    
                    data_manager.update_patient(selected_patient, updated_data)
                    st.success("Patient information updated successfully!")
                    st.rerun()
    else:
        st.info("No patients available to edit.")

elif operation == "Search Patients":
    st.header("🔍 Search Patients")
    
    search_query = st.text_input("Search by name, email, or phone number", placeholder="Enter search term...")
    
    if search_query:
        results = data_manager.search_patients(search_query)
        
        if results:
            st.write(f"Found {len(results)} patient(s):")
            
            for patient in results:
                with st.expander(f"👤 {patient['name']} - {patient['email']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Phone:** {patient.get('phone', 'N/A')}")
                        st.write(f"**Date of Birth:** {patient.get('date_of_birth', 'N/A')}")
                        st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
                        st.write(f"**Blood Group:** {patient.get('blood_group', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Emergency Contact:** {patient.get('emergency_contact', 'N/A')}")
                        st.write(f"**Insurance:** {patient.get('insurance_info', 'N/A')}")
                        st.write(f"**Address:** {patient.get('address', 'N/A')}")
                    
                    if patient.get('medical_history'):
                        st.write(f"**Medical History:** {patient['medical_history']}")
                    
                    if patient.get('current_medications'):
                        st.write(f"**Current Medications:** {patient['current_medications']}")
        else:
            st.info("No patients found matching your search criteria.")
    
    else:
        st.info("Enter a search term to find patients.")

# Footer
st.markdown("---")
st.markdown("💡 **Tips:** Use the sidebar to navigate between different patient management operations. All patient data is stored securely in the session.")
