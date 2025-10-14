import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import plotly.graph_objects as go
from utils.db_manager import DatabaseManager
from utils.auth import init_auth, require_auth, is_authenticated

# Initialize database manager
@st.cache_resource
def get_data_manager():
    return DatabaseManager()

data_manager = get_data_manager()

st.set_page_config(page_title="Appointments - HealthSense", page_icon="📅", layout="wide")

# Initialize authentication
init_auth()
require_auth()

st.title("📅 Appointment Management System")
st.markdown("---")

# Sidebar for operations
st.sidebar.header("Appointment Operations")
operation = st.sidebar.selectbox(
    "Select Operation",
    ["View Calendar", "Schedule Appointment", "Manage Appointments", "Today's Schedule"]
)

if operation == "View Calendar":
    st.header("📅 Appointment Calendar")
    
    # Date selector
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_date = st.date_input("Select Date", value=datetime.now().date())
        view_mode = st.radio("View Mode", ["Day", "Week"])
    
    with col2:
        appointments = data_manager.get_appointments()
        
        if view_mode == "Day":
            daily_appointments = data_manager.get_appointments_by_date(selected_date.isoformat())
            
            st.subheader(f"Appointments for {selected_date.strftime('%B %d, %Y')}")
            
            if daily_appointments:
                for apt in sorted(daily_appointments, key=lambda x: x['time']):
                    with st.container():
                        col_time, col_patient, col_doctor, col_status = st.columns([1, 2, 2, 1])
                        
                        with col_time:
                            st.write(f"🕐 **{apt['time']}**")
                        
                        with col_patient:
                            st.write(f"👤 {apt['patient_name']}")
                        
                        with col_doctor:
                            st.write(f"👨‍⚕️ Dr. {apt['doctor']}")
                        
                        with col_status:
                            status_color = {
                                'Scheduled': '🔵',
                                'Completed': '✅',
                                'Cancelled': '❌',
                                'No-show': '⚠️'
                            }
                            st.write(f"{status_color.get(apt['status'], '🔵')} {apt['status']}")
                        
                        st.markdown("---")
            else:
                st.info("No appointments scheduled for this date.")
        
        else:  # Week view
            week_start = selected_date - timedelta(days=selected_date.weekday())
            week_dates = [week_start + timedelta(days=i) for i in range(7)]
            
            st.subheader(f"Week of {week_start.strftime('%B %d, %Y')}")
            
            # Create week view
            cols = st.columns(7)
            
            for i, day_date in enumerate(week_dates):
                with cols[i]:
                    st.write(f"**{day_date.strftime('%a %d')}**")
                    day_appointments = data_manager.get_appointments_by_date(day_date.isoformat())
                    
                    if day_appointments:
                        for apt in sorted(day_appointments, key=lambda x: x['time'])[:3]:  # Show max 3
                            st.write(f"🕐 {apt['time']}")
                            st.write(f"👤 {apt['patient_name'][:15]}...")
                            st.write("---")
                        if len(day_appointments) > 3:
                            st.write(f"... +{len(day_appointments) - 3} more")
                    else:
                        st.write("No appointments")

elif operation == "Schedule Appointment":
    st.header("➕ Schedule New Appointment")
    
    patients = data_manager.get_patients()
    
    if not patients:
        st.warning("No patients available. Please add patients first.")
    else:
        with st.form("schedule_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_patient = st.selectbox(
                    "Select Patient *",
                    options=[p['id'] for p in patients],
                    format_func=lambda x: next(p['name'] for p in patients if p['id'] == x)
                )
                
                appointment_date = st.date_input("Appointment Date *", min_value=date.today())
                appointment_time = st.time_input("Appointment Time *")
                
            with col2:
                doctors = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
                doctor = st.selectbox("Doctor *", doctors)
                
                departments = ["General Medicine", "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Dermatology"]
                department = st.selectbox("Department", departments)
                
                appointment_type = st.selectbox("Appointment Type", ["Consultation", "Follow-up", "Check-up", "Treatment"])
            
            notes = st.text_area("Notes", placeholder="Any special instructions or notes...")
            
            submitted = st.form_submit_button("Schedule Appointment", type="primary")
            
            if submitted:
                patient = data_manager.get_patient_by_id(selected_patient)
                
                appointment_data = {
                    'patient_id': selected_patient,
                    'patient_name': patient['name'],
                    'doctor': doctor,
                    'department': department,
                    'date': appointment_date.isoformat(),
                    'time': appointment_time.strftime("%H:%M"),
                    'type': appointment_type,
                    'status': 'Scheduled',
                    'notes': notes
                }
                
                appointment_id = data_manager.add_appointment(appointment_data)
                st.success(f"Appointment scheduled successfully! ID: {appointment_id}")
                st.success(f"📅 {patient['name']} with Dr. {doctor} on {appointment_date} at {appointment_time}")
                st.balloons()

elif operation == "Manage Appointments":
    st.header("🛠️ Manage Appointments")
    
    appointments = data_manager.get_appointments()
    
    if appointments:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "Completed", "Cancelled", "No-show"])
        
        with col2:
            date_from = st.date_input("From Date", value=datetime.now().date() - timedelta(days=7))
        
        with col3:
            date_to = st.date_input("To Date", value=datetime.now().date() + timedelta(days=30))
        
        # Apply filters
        filtered_appointments = []
        for apt in appointments:
            apt_date = datetime.fromisoformat(apt['date']).date()
            
            if date_from <= apt_date <= date_to:
                if status_filter == "All" or apt['status'] == status_filter:
                    filtered_appointments.append(apt)
        
        st.subheader(f"Found {len(filtered_appointments)} appointments")
        
        # Display appointments
        for i, apt in enumerate(filtered_appointments):
            with st.expander(f"📅 {apt['date']} {apt['time']} - {apt['patient_name']} with Dr. {apt['doctor']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Patient:** {apt['patient_name']}")
                    st.write(f"**Doctor:** Dr. {apt['doctor']}")
                    st.write(f"**Department:** {apt.get('department', 'N/A')}")
                    st.write(f"**Type:** {apt.get('type', 'N/A')}")
                    st.write(f"**Date & Time:** {apt['date']} at {apt['time']}")
                    if apt.get('notes'):
                        st.write(f"**Notes:** {apt['notes']}")
                
                with col2:
                    st.write(f"**Current Status:** {apt['status']}")
                    
                    new_status = st.selectbox(
                        "Change Status",
                        ["Scheduled", "Completed", "Cancelled", "No-show"],
                        index=["Scheduled", "Completed", "Cancelled", "No-show"].index(apt['status']),
                        key=f"status_{apt['id']}"
                    )
                    
                    if st.button(f"Update Status", key=f"update_{apt['id']}"):
                        data_manager.update_appointment_status(apt['id'], new_status)
                        st.success("Status updated successfully!")
                        st.rerun()
                    
                    if st.button(f"Delete Appointment", key=f"delete_{apt['id']}", type="secondary"):
                        data_manager.delete_appointment(apt['id'])
                        st.success("Appointment deleted successfully!")
                        st.rerun()
    else:
        st.info("No appointments found.")

elif operation == "Today's Schedule":
    st.header("📋 Today's Schedule")
    
    today = datetime.now().date().isoformat()
    today_appointments = data_manager.get_appointments_by_date(today)
    
    if today_appointments:
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Appointments", len(today_appointments))
        
        with col2:
            scheduled_count = len([a for a in today_appointments if a['status'] == 'Scheduled'])
            st.metric("Scheduled", scheduled_count)
        
        with col3:
            completed_count = len([a for a in today_appointments if a['status'] == 'Completed'])
            st.metric("Completed", completed_count)
        
        with col4:
            cancelled_count = len([a for a in today_appointments if a['status'] in ['Cancelled', 'No-show']])
            st.metric("Cancelled/No-show", cancelled_count)
        
        st.markdown("---")
        
        # Timeline view
        st.subheader("🕐 Today's Timeline")
        
        # Sort appointments by time
        sorted_appointments = sorted(today_appointments, key=lambda x: x['time'])
        
        for apt in sorted_appointments:
            status_color = {
                'Scheduled': '🔵',
                'Completed': '✅',
                'Cancelled': '❌',
                'No-show': '⚠️'
            }
            
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
            
            with col1:
                st.write(f"**{apt['time']}**")
            
            with col2:
                st.write(f"👤 {apt['patient_name']}")
            
            with col3:
                st.write(f"👨‍⚕️ Dr. {apt['doctor']}")
            
            with col4:
                st.write(f"{apt.get('type', 'Consultation')}")
            
            with col5:
                st.write(f"{status_color.get(apt['status'], '🔵')} {apt['status']}")
            
            st.markdown("---")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Mark All Scheduled as Completed", type="primary"):
                for apt in today_appointments:
                    if apt['status'] == 'Scheduled':
                        data_manager.update_appointment_status(apt['id'], 'Completed')
                st.success("All scheduled appointments marked as completed!")
                st.rerun()
        
        with col2:
            if st.button("Generate Daily Report", type="secondary"):
                st.info("Daily report functionality would be implemented here.")
    
    else:
        st.info("No appointments scheduled for today.")
        
        if st.button("Schedule First Appointment Today"):
            st.switch_page("pages/2_Appointments.py")

# Footer
st.markdown("---")
st.markdown("💡 **Tips:** Use the calendar view to get an overview of scheduled appointments. You can quickly update appointment statuses from the manage section.")
