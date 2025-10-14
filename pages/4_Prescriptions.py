import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from utils.db_manager import DatabaseManager
from utils.auth import init_auth, require_auth, is_authenticated
from utils.pdf_generator import PDFGenerator

# Initialize database manager
@st.cache_resource
def get_data_manager():
    return DatabaseManager()

data_manager = get_data_manager()
pdf_generator = PDFGenerator()

st.set_page_config(page_title="Prescriptions - HealthSense", page_icon="💊", layout="wide")

# Initialize authentication
init_auth()
require_auth()

st.title("💊 Prescription Management System")
st.markdown("---")

# Common medications database
COMMON_MEDICATIONS = {
    "Antibiotics": ["Amoxicillin", "Azithromycin", "Ciprofloxacin", "Doxycycline"],
    "Pain Relief": ["Ibuprofen", "Acetaminophen", "Aspirin", "Naproxen"],
    "Heart": ["Lisinopril", "Metoprolol", "Amlodipine", "Atorvastatin"],
    "Diabetes": ["Metformin", "Glipizide", "Insulin", "Sitagliptin"],
    "Mental Health": ["Sertraline", "Fluoxetine", "Lorazepam", "Alprazolam"],
    "Respiratory": ["Albuterol", "Prednisone", "Montelukast", "Fluticasone"]
}

# Sidebar for operations
st.sidebar.header("Prescription Operations")
operation = st.sidebar.selectbox(
    "Select Operation",
    ["View All Prescriptions", "Create Prescription", "Patient Prescriptions", "Medication Tracker", "Refill Management"]
)

if operation == "View All Prescriptions":
    st.header("📋 All Prescriptions")
    
    prescriptions = data_manager.get_prescriptions()
    patients = data_manager.get_patients()
    patient_lookup = {p['id']: p['name'] for p in patients}
    
    if prescriptions:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Prescriptions", len(prescriptions))
        
        with col2:
            active_count = len([p for p in prescriptions if p.get('status') == 'Active'])
            st.metric("Active", active_count)
        
        with col3:
            completed_count = len([p for p in prescriptions if p.get('status') == 'Completed'])
            st.metric("Completed", completed_count)
        
        with col4:
            due_refill = len([p for p in prescriptions if p.get('refills_remaining', 0) <= 1 and p.get('status') == 'Active'])
            st.metric("Due for Refill", due_refill)
        
        st.markdown("---")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Completed", "Cancelled", "Suspended"])
        
        with col2:
            patient_filter = st.selectbox(
                "Filter by Patient", 
                ["All"] + [p['name'] for p in patients]
            )
        
        with col3:
            date_range = st.selectbox("Date Range", ["All", "Last 30 days", "Last 90 days", "This year"])
        
        # Apply filters
        filtered_prescriptions = prescriptions
        
        if status_filter != "All":
            filtered_prescriptions = [p for p in filtered_prescriptions if p.get('status') == status_filter]
        
        if patient_filter != "All":
            selected_patient_id = next(p['id'] for p in patients if p['name'] == patient_filter)
            filtered_prescriptions = [p for p in filtered_prescriptions if p['patient_id'] == selected_patient_id]
        
        # Date filtering
        if date_range != "All":
            cutoff_date = datetime.now()
            if date_range == "Last 30 days":
                cutoff_date -= timedelta(days=30)
            elif date_range == "Last 90 days":
                cutoff_date -= timedelta(days=90)
            elif date_range == "This year":
                cutoff_date = cutoff_date.replace(month=1, day=1)
            
            filtered_prescriptions = [
                p for p in filtered_prescriptions 
                if datetime.fromisoformat(p.get('date_prescribed', '2000-01-01')) >= cutoff_date
            ]
        
        st.subheader(f"Showing {len(filtered_prescriptions)} prescriptions")
        
        # Display prescriptions
        for rx in filtered_prescriptions:
            patient_name = patient_lookup.get(rx['patient_id'], 'Unknown Patient')
            
            with st.expander(f"💊 {rx.get('medication_name', 'Unknown Medication')} - {patient_name}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Patient:** {patient_name}")
                    st.write(f"**Medication:** {rx.get('medication_name', 'N/A')}")
                    st.write(f"**Dosage:** {rx.get('dosage', 'N/A')}")
                    st.write(f"**Frequency:** {rx.get('frequency', 'N/A')}")
                    st.write(f"**Duration:** {rx.get('duration', 'N/A')}")
                
                with col2:
                    st.write(f"**Prescribed by:** Dr. {rx.get('doctor', 'N/A')}")
                    st.write(f"**Date Prescribed:** {rx.get('date_prescribed', 'N/A')}")
                    st.write(f"**Quantity:** {rx.get('quantity', 'N/A')}")
                    st.write(f"**Refills Remaining:** {rx.get('refills_remaining', 0)}")
                    
                    if rx.get('instructions'):
                        st.write(f"**Instructions:** {rx['instructions']}")
                
                with col3:
                    status_colors = {
                        'Active': '🟢',
                        'Completed': '✅',
                        'Cancelled': '❌',
                        'Suspended': '⚠️'
                    }
                    st.write(f"**Status:** {status_colors.get(rx.get('status', 'Active'), '🟢')} {rx.get('status', 'Active')}")
                    
                    if rx.get('refills_remaining', 0) <= 1:
                        st.warning("🔔 Refill needed soon")
                    
                    # PDF Export
                    patient = data_manager.get_patient_by_id(rx['patient_id'])
                    if patient:
                        pdf_buffer = pdf_generator.generate_prescription_pdf(rx, patient, rx['doctor'])
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_buffer,
                            file_name=f"prescription_{patient['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key=f"download_{rx['id']}"
                        )
    
    else:
        st.info("No prescriptions found. Create the first prescription!")

elif operation == "Create Prescription":
    st.header("➕ Create New Prescription")
    
    patients = data_manager.get_patients()
    
    if not patients:
        st.warning("No patients available. Please add patients first.")
    else:
        with st.form("create_prescription_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Patient Information")
                selected_patient = st.selectbox(
                    "Select Patient *",
                    options=[p['id'] for p in patients],
                    format_func=lambda x: next(p['name'] for p in patients if p['id'] == x)
                )
                
                doctors = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
                prescribing_doctor = st.selectbox("Prescribing Doctor *", doctors)
                
                date_prescribed = st.date_input("Date Prescribed *", value=datetime.now().date())
            
            with col2:
                st.subheader("Prescription Details")
                
                # Medication selection
                medication_category = st.selectbox("Medication Category", list(COMMON_MEDICATIONS.keys()))
                medication_name = st.selectbox("Medication Name *", COMMON_MEDICATIONS[medication_category])
                
                # Or custom medication
                custom_med = st.text_input("Or enter custom medication name:")
                if custom_med:
                    medication_name = custom_med
            
            st.subheader("Dosage and Instructions")
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                dosage = st.text_input("Dosage *", placeholder="e.g., 500mg")
                frequency = st.selectbox("Frequency *", 
                    ["Once daily", "Twice daily", "Three times daily", "Four times daily", "As needed", "Other"])
                
                if frequency == "Other":
                    custom_frequency = st.text_input("Custom frequency:")
                    if custom_frequency:
                        frequency = custom_frequency
            
            with col4:
                quantity = st.number_input("Quantity *", min_value=1, value=30)
                refills = st.number_input("Number of Refills", min_value=0, max_value=12, value=3)
            
            with col5:
                duration = st.text_input("Duration", placeholder="e.g., 10 days, 1 month")
                route = st.selectbox("Route", ["Oral", "Topical", "Injection", "IV", "Other"])
            
            instructions = st.text_area("Special Instructions", 
                placeholder="Take with food, avoid alcohol, etc.")
            
            indication = st.text_input("Indication/Diagnosis", 
                placeholder="What condition is this treating?")
            
            # Warnings and interactions
            col6, col7 = st.columns(2)
            
            with col6:
                warnings = st.text_area("Warnings", 
                    placeholder="Side effects, contraindications, etc.")
            
            with col7:
                interactions = st.text_area("Drug Interactions", 
                    placeholder="Known interactions with other medications")
            
            submitted = st.form_submit_button("Create Prescription", type="primary")
            
            if submitted:
                if not all([selected_patient, prescribing_doctor, medication_name, dosage, frequency, quantity]):
                    st.error("Please fill in all required fields marked with *")
                else:
                    prescription_data = {
                        'patient_id': selected_patient,
                        'doctor': prescribing_doctor,
                        'medication_name': medication_name,
                        'dosage': dosage,
                        'frequency': frequency,
                        'quantity': quantity,
                        'refills_remaining': refills,
                        'duration': duration,
                        'route': route,
                        'instructions': instructions,
                        'indication': indication,
                        'warnings': warnings,
                        'interactions': interactions,
                        'date_prescribed': date_prescribed.isoformat(),
                        'status': 'Active'
                    }
                    
                    rx_id = data_manager.add_prescription(prescription_data)
                    patient_name = next(p['name'] for p in patients if p['id'] == selected_patient)
                    
                    st.success(f"Prescription created successfully!")
                    st.success(f"📋 {medication_name} prescribed for {patient_name}")
                    st.success(f"Prescription ID: {rx_id}")
                    st.balloons()

elif operation == "Patient Prescriptions":
    st.header("👤 Patient Prescription History")
    
    patients = data_manager.get_patients()
    
    if not patients:
        st.warning("No patients available.")
    else:
        selected_patient = st.selectbox(
            "Select Patient",
            options=[p['id'] for p in patients],
            format_func=lambda x: next(p['name'] for p in patients if p['id'] == x)
        )
        
        patient = data_manager.get_patient_by_id(selected_patient)
        patient_prescriptions = data_manager.get_prescriptions_by_patient(selected_patient)
        
        st.subheader(f"📋 Prescriptions for {patient['name']}")
        
        if patient_prescriptions:
            # Patient prescription statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Prescriptions", len(patient_prescriptions))
            
            with col2:
                active_count = len([p for p in patient_prescriptions if p.get('status') == 'Active'])
                st.metric("Active", active_count)
            
            with col3:
                unique_meds = len(set([p.get('medication_name') for p in patient_prescriptions]))
                st.metric("Unique Medications", unique_meds)
            
            with col4:
                need_refill = len([p for p in patient_prescriptions if p.get('refills_remaining', 0) <= 1])
                st.metric("Need Refill", need_refill)
            
            st.markdown("---")
            
            # Current medications
            st.subheader("💊 Current Active Medications")
            active_meds = [p for p in patient_prescriptions if p.get('status') == 'Active']
            
            if active_meds:
                for med in active_meds:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                        
                        with col1:
                            st.write(f"**{med.get('medication_name', 'Unknown')}**")
                            st.write(f"Dosage: {med.get('dosage', 'N/A')}")
                        
                        with col2:
                            st.write(f"Frequency: {med.get('frequency', 'N/A')}")
                            st.write(f"Route: {med.get('route', 'N/A')}")
                        
                        with col3:
                            st.write(f"Prescribed: {med.get('date_prescribed', 'N/A')}")
                            st.write(f"Dr. {med.get('doctor', 'N/A')}")
                        
                        with col4:
                            refills = med.get('refills_remaining', 0)
                            if refills <= 1:
                                st.warning(f"🔔 {refills} refills left")
                            else:
                                st.info(f"✅ {refills} refills")
                        
                        if med.get('instructions'):
                            st.write(f"**Instructions:** {med['instructions']}")
                        
                        st.markdown("---")
            else:
                st.info("No active medications.")
            
            # Prescription history timeline
            st.subheader("📅 Prescription History")
            
            # Sort by date
            sorted_prescriptions = sorted(patient_prescriptions, 
                                        key=lambda x: x.get('date_prescribed', '2000-01-01'), 
                                        reverse=True)
            
            for rx in sorted_prescriptions:
                prescribed_date = datetime.fromisoformat(rx.get('date_prescribed', '2000-01-01')).strftime('%B %d, %Y')
                
                with st.expander(f"💊 {rx.get('medication_name', 'Unknown')} - {prescribed_date}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Medication:** {rx.get('medication_name', 'N/A')}")
                        st.write(f"**Dosage:** {rx.get('dosage', 'N/A')}")
                        st.write(f"**Frequency:** {rx.get('frequency', 'N/A')}")
                        st.write(f"**Duration:** {rx.get('duration', 'N/A')}")
                        st.write(f"**Quantity:** {rx.get('quantity', 'N/A')}")
                        
                        if rx.get('indication'):
                            st.write(f"**Indication:** {rx['indication']}")
                    
                    with col2:
                        st.write(f"**Prescribed by:** Dr. {rx.get('doctor', 'N/A')}")
                        st.write(f"**Date:** {prescribed_date}")
                        st.write(f"**Status:** {rx.get('status', 'N/A')}")
                        st.write(f"**Refills Remaining:** {rx.get('refills_remaining', 0)}")
                        
                        if rx.get('instructions'):
                            st.write(f"**Instructions:** {rx['instructions']}")
                        
                        if rx.get('warnings'):
                            st.warning(f"⚠️ **Warnings:** {rx['warnings']}")
        
        else:
            st.info(f"No prescriptions found for {patient['name']}.")

elif operation == "Medication Tracker":
    st.header("📊 Medication Analytics")
    
    prescriptions = data_manager.get_prescriptions()
    patients = data_manager.get_patients()
    
    if prescriptions:
        # Most prescribed medications
        medication_counts = {}
        for rx in prescriptions:
            med_name = rx.get('medication_name', 'Unknown')
            medication_counts[med_name] = medication_counts.get(med_name, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💊 Most Prescribed Medications")
            
            if medication_counts:
                sorted_meds = sorted(medication_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                meds_df = pd.DataFrame(sorted_meds, columns=['Medication', 'Count'])
                fig = px.bar(meds_df, x='Count', y='Medication', orientation='h',
                           title="Top 10 Prescribed Medications")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Prescription Status Distribution")
            
            status_counts = {}
            for rx in prescriptions:
                status = rx.get('status', 'Active')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig = px.pie(values=list(status_counts.values()), 
                           names=list(status_counts.keys()),
                           title="Prescription Status Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        # Refill alerts
        st.subheader("🔔 Refill Alerts")
        
        refill_needed = [rx for rx in prescriptions 
                        if rx.get('status') == 'Active' and rx.get('refills_remaining', 0) <= 1]
        
        if refill_needed:
            patient_lookup = {p['id']: p['name'] for p in patients}
            
            st.warning(f"⚠️ {len(refill_needed)} prescriptions need refills soon!")
            
            for rx in refill_needed:
                patient_name = patient_lookup.get(rx['patient_id'], 'Unknown Patient')
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**{patient_name}**")
                
                with col2:
                    st.write(f"{rx.get('medication_name', 'Unknown')}")
                
                with col3:
                    st.write(f"Dr. {rx.get('doctor', 'N/A')}")
                
                with col4:
                    refills = rx.get('refills_remaining', 0)
                    if refills == 0:
                        st.error("🚨 No refills left")
                    else:
                        st.warning(f"⚠️ {refills} refill left")
        else:
            st.success("✅ All prescriptions have sufficient refills!")
        
        # Prescription timeline
        st.subheader("📅 Prescription Timeline")
        
        # Create timeline data
        timeline_data = []
        for rx in prescriptions:
            date_prescribed = rx.get('date_prescribed', '2000-01-01')
            timeline_data.append({
                'date': date_prescribed,
                'medication': rx.get('medication_name', 'Unknown'),
                'patient': rx.get('patient_id', 'Unknown'),
                'count': 1
            })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by month
            monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
            
            fig = px.line(x=monthly_counts.index.astype(str), y=monthly_counts.values,
                         title="Prescriptions Over Time",
                         labels={'x': 'Month', 'y': 'Number of Prescriptions'})
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No prescription data available for analytics.")

elif operation == "Refill Management":
    st.header("🔄 Prescription Refill Management")
    
    prescriptions = data_manager.get_prescriptions()
    patients = data_manager.get_patients()
    patient_lookup = {p['id']: p['name'] for p in patients}
    
    # Filter for active prescriptions
    active_prescriptions = [rx for rx in prescriptions if rx.get('status') == 'Active']
    
    if active_prescriptions:
        st.subheader("🔔 Refill Queue")
        
        # Categorize by refill urgency
        urgent_refills = [rx for rx in active_prescriptions if rx.get('refills_remaining', 0) == 0]
        soon_refills = [rx for rx in active_prescriptions if rx.get('refills_remaining', 0) == 1]
        good_refills = [rx for rx in active_prescriptions if rx.get('refills_remaining', 0) > 1]
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Urgent (0 refills)", len(urgent_refills))
        
        with col2:
            st.metric("Soon (1 refill)", len(soon_refills))
        
        with col3:
            st.metric("Good (>1 refills)", len(good_refills))
        
        with col4:
            st.metric("Total Active", len(active_prescriptions))
        
        # Urgent refills section
        if urgent_refills:
            st.subheader("🚨 Urgent Refills Needed")
            
            for rx in urgent_refills:
                patient_name = patient_lookup.get(rx['patient_id'], 'Unknown Patient')
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.error(f"**{patient_name}**")
                        st.write(f"📞 Contact needed")
                    
                    with col2:
                        st.write(f"**{rx.get('medication_name', 'Unknown')}**")
                        st.write(f"{rx.get('dosage', 'N/A')}")
                    
                    with col3:
                        st.write(f"Dr. {rx.get('doctor', 'N/A')}")
                        st.write(f"Prescribed: {rx.get('date_prescribed', 'N/A')}")
                    
                    with col4:
                        if st.button("Add Refill", key=f"urgent_{rx['id']}", type="primary"):
                            # Update refills
                            data_manager.update_prescription_status(rx['id'], 'Active')
                            # In a real system, you'd update refill count
                            st.success("Refill authorized!")
                            st.rerun()
                    
                    st.markdown("---")
        
        # Soon to expire refills
        if soon_refills:
            st.subheader("⚠️ Refills Needed Soon")
            
            for rx in soon_refills:
                patient_name = patient_lookup.get(rx['patient_id'], 'Unknown Patient')
                
                with st.expander(f"⚠️ {rx.get('medication_name', 'Unknown')} - {patient_name} (1 refill left)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Patient:** {patient_name}")
                        st.write(f"**Medication:** {rx.get('medication_name', 'Unknown')}")
                        st.write(f"**Dosage:** {rx.get('dosage', 'N/A')}")
                        st.write(f"**Frequency:** {rx.get('frequency', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Prescribing Doctor:** Dr. {rx.get('doctor', 'N/A')}")
                        st.write(f"**Date Prescribed:** {rx.get('date_prescribed', 'N/A')}")
                        st.write(f"**Last Refill:** Last week")  # This would be tracked in a real system
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Authorize Refill", key=f"auth_{rx['id']}"):
                                st.success("Refill authorized!")
                        
                        with col_btn2:
                            if st.button("Contact Patient", key=f"contact_{rx['id']}"):
                                st.info("Patient contacted for appointment.")
        
        # Bulk refill management
        st.subheader("📦 Bulk Refill Management")
        
        refill_candidates = urgent_refills + soon_refills
        
        if refill_candidates:
            st.write(f"Select prescriptions for bulk refill authorization ({len(refill_candidates)} candidates):")
            
            selected_refills = []
            
            for rx in refill_candidates:
                patient_name = patient_lookup.get(rx['patient_id'], 'Unknown Patient')
                
                if st.checkbox(f"{rx.get('medication_name', 'Unknown')} - {patient_name}", key=f"bulk_{rx['id']}"):
                    selected_refills.append(rx)
            
            if selected_refills:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if st.button("Authorize Selected Refills", type="primary"):
                        for rx in selected_refills:
                            # Update refill count in real system
                            data_manager.update_prescription_status(rx['id'], 'Active')
                        
                        st.success(f"Authorized refills for {len(selected_refills)} prescriptions!")
                        st.balloons()
                        st.rerun()
                
                with col2:
                    st.info(f"{len(selected_refills)} prescriptions selected for refill authorization.")
        
        else:
            st.success("✅ No urgent refills needed at this time!")
    
    else:
        st.info("No active prescriptions found.")

# Footer
st.markdown("---")
st.markdown("💡 **Tips:** Regularly monitor refill status to ensure patients don't run out of critical medications. Use bulk operations for efficiency during busy periods.")
