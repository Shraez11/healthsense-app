import streamlit as st
import pandas as pd
from datetime import datetime
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

st.set_page_config(page_title="Medical Records - HealthSense", page_icon="📋", layout="wide")

# Initialize authentication
init_auth()
require_auth()

st.title("📋 Medical Records Management")
st.markdown("---")

# Sidebar for operations
st.sidebar.header("Medical Records Operations")
operation = st.sidebar.selectbox(
    "Select Operation",
    ["View All Records", "Add Medical Record", "Patient Records", "Lab Results", "Document Upload"]
)

if operation == "View All Records":
    st.header("📁 All Medical Records")
    
    records = data_manager.get_medical_records()
    patients = data_manager.get_patients()
    
    if records:
        # Create patient lookup for display
        patient_lookup = {p['id']: p['name'] for p in patients}
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        df['patient_name'] = df['patient_id'].map(patient_lookup)
        
        # Display summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(records))
        
        with col2:
            lab_results = len([r for r in records if r.get('record_type') == 'Lab Result'])
            st.metric("Lab Results", lab_results)
        
        with col3:
            diagnoses = len([r for r in records if r.get('record_type') == 'Diagnosis'])
            st.metric("Diagnoses", diagnoses)
        
        with col4:
            treatments = len([r for r in records if r.get('record_type') == 'Treatment'])
            st.metric("Treatments", treatments)
        
        st.markdown("---")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            record_type_filter = st.selectbox("Filter by Type", ["All", "Lab Result", "Diagnosis", "Treatment", "Imaging", "Other"])
        
        with col2:
            patient_filter = st.selectbox(
                "Filter by Patient", 
                ["All"] + [p['name'] for p in patients],
                key="patient_filter_all_records"
            )
        
        # Apply filters
        filtered_records = records
        
        if record_type_filter != "All":
            filtered_records = [r for r in filtered_records if r.get('record_type') == record_type_filter]
        
        if patient_filter != "All":
            selected_patient_id = next(p['id'] for p in patients if p['name'] == patient_filter)
            filtered_records = [r for r in filtered_records if r['patient_id'] == selected_patient_id]
        
        st.subheader(f"Showing {len(filtered_records)} records")
        
        # Display records
        for record in filtered_records:
            patient_name = patient_lookup.get(record['patient_id'], 'Unknown Patient')
            
            with st.expander(f"📋 {record.get('title', 'Medical Record')} - {patient_name} ({record.get('date', 'No date')})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Patient:** {patient_name}")
                    st.write(f"**Type:** {record.get('record_type', 'N/A')}")
                    st.write(f"**Date:** {record.get('date', 'N/A')}")
                    st.write(f"**Doctor:** Dr. {record.get('doctor', 'N/A')}")
                    
                    if record.get('description'):
                        st.write(f"**Description:**")
                        st.write(record['description'])
                    
                    if record.get('findings'):
                        st.write(f"**Findings:**")
                        st.write(record['findings'])
                    
                    if record.get('recommendations'):
                        st.write(f"**Recommendations:**")
                        st.write(record['recommendations'])
                
                with col2:
                    st.write(f"**Status:** {record.get('status', 'N/A')}")
                    if record.get('priority'):
                        priority_colors = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
                        st.write(f"**Priority:** {priority_colors.get(record['priority'], '')} {record['priority']}")
                    
                    if record.get('file_path'):
                        st.write("📎 **Attachment:** File uploaded")
                    
                    if record.get('lab_values'):
                        st.write("🧪 **Lab Values Available**")
                    
                    # PDF Export
                    patient = data_manager.get_patient_by_id(record['patient_id'])
                    if patient:
                        pdf_buffer = pdf_generator.generate_medical_report_pdf(record, patient)
                        st.download_button(
                            label="📄 Download PDF",
                            data=pdf_buffer,
                            file_name=f"medical_report_{patient['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key=f"download_record_{record['id']}"
                        )
    
    else:
        st.info("No medical records found. Add the first record using the sidebar.")

elif operation == "Add Medical Record":
    st.header("➕ Add New Medical Record")
    
    patients = data_manager.get_patients()
    
    if not patients:
        st.warning("No patients available. Please add patients first.")
    else:
        with st.form("add_medical_record_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_patient = st.selectbox(
                    "Select Patient *",
                    options=[p['id'] for p in patients],
                    format_func=lambda x: next(p['name'] for p in patients if p['id'] == x)
                )
                
                record_type = st.selectbox(
                    "Record Type *",
                    ["Lab Result", "Diagnosis", "Treatment", "Imaging", "Surgery", "Consultation", "Other"]
                )
                
                title = st.text_input("Record Title *", placeholder="e.g., Blood Test Results")
                
                record_date = st.date_input("Date *", value=datetime.now().date())
                
            with col2:
                doctors = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
                doctor = st.selectbox("Doctor *", doctors)
                
                priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                
                status = st.selectbox("Status", ["Active", "Completed", "Under Review", "Cancelled"])
                
                department = st.selectbox("Department", 
                    ["General Medicine", "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Laboratory"])
            
            description = st.text_area("Description", placeholder="Detailed description of the medical record...")
            
            findings = st.text_area("Findings/Results", placeholder="Key findings, test results, observations...")
            
            recommendations = st.text_area("Recommendations", placeholder="Treatment recommendations, follow-up instructions...")
            
            # Lab values section (for lab results)
            if st.checkbox("Add Lab Values"):
                st.write("**Lab Values:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=0.0, step=0.1)
                    white_blood_cells = st.number_input("WBC (×10³/μL)", min_value=0.0, step=0.1)
                
                with col2:
                    glucose = st.number_input("Glucose (mg/dL)", min_value=0.0, step=1.0)
                    cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=0.0, step=1.0)
                
                with col3:
                    blood_pressure_sys = st.number_input("BP Systolic", min_value=0, step=1)
                    blood_pressure_dia = st.number_input("BP Diastolic", min_value=0, step=1)
            
            # File upload placeholder
            uploaded_file = st.file_uploader(
                "Upload Document/Image", 
                type=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
                help="Upload related documents, images, or reports"
            )
            
            submitted = st.form_submit_button("Add Medical Record", type="primary")
            
            if submitted:
                if not all([selected_patient, record_type, title, record_date, doctor]):
                    st.error("Please fill in all required fields marked with *")
                else:
                    record_data = {
                        'patient_id': selected_patient,
                        'record_type': record_type,
                        'title': title,
                        'date': record_date.isoformat(),
                        'doctor': doctor,
                        'department': department,
                        'priority': priority,
                        'status': status,
                        'description': description,
                        'findings': findings,
                        'recommendations': recommendations
                    }
                    
                    # Add lab values if provided
                    if st.session_state.get('add_lab_values', False):
                        lab_values = {
                            'hemoglobin': hemoglobin,
                            'white_blood_cells': white_blood_cells,
                            'glucose': glucose,
                            'cholesterol': cholesterol,
                            'blood_pressure': f"{blood_pressure_sys}/{blood_pressure_dia}"
                        }
                        record_data['lab_values'] = lab_values
                    
                    # Handle file upload (in a real app, you'd save this to storage)
                    if uploaded_file:
                        record_data['file_name'] = uploaded_file.name
                        record_data['file_type'] = uploaded_file.type
                        record_data['file_size'] = uploaded_file.size
                    
                    record_id = data_manager.add_medical_record(record_data)
                    patient_name = next(p['name'] for p in patients if p['id'] == selected_patient)
                    
                    st.success(f"Medical record added successfully for {patient_name}!")
                    st.success(f"Record ID: {record_id}")
                    st.balloons()

elif operation == "Patient Records":
    st.header("👤 Patient Medical Records")
    
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
        patient_records = data_manager.get_medical_records_by_patient(selected_patient)
        
        # Patient info header
        st.subheader(f"📋 Medical Records for {patient['name']}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(patient_records))
        with col2:
            st.metric("Age", patient.get('age', 'N/A'))
        with col3:
            st.metric("Blood Group", patient.get('blood_group', 'N/A'))
        with col4:
            recent_records = len([r for r in patient_records if 
                                datetime.fromisoformat(r.get('date', '2000-01-01')) > datetime.now() - pd.Timedelta(days=30)])
            st.metric("Recent (30 days)", recent_records)
        
        if patient_records:
            # Timeline view
            st.subheader("📅 Medical Timeline")
            
            # Sort records by date
            sorted_records = sorted(patient_records, key=lambda x: x.get('date', '2000-01-01'), reverse=True)
            
            for record in sorted_records:
                record_date = datetime.fromisoformat(record.get('date', '2000-01-01')).strftime('%B %d, %Y')
                
                with st.expander(f"📋 {record.get('title', 'Medical Record')} - {record_date}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Type:** {record.get('record_type', 'N/A')}")
                        st.write(f"**Doctor:** Dr. {record.get('doctor', 'N/A')}")
                        st.write(f"**Department:** {record.get('department', 'N/A')}")
                        
                        if record.get('description'):
                            st.write(f"**Description:** {record['description']}")
                        
                        if record.get('findings'):
                            st.write(f"**Findings:** {record['findings']}")
                        
                        if record.get('recommendations'):
                            st.write(f"**Recommendations:** {record['recommendations']}")
                        
                        # Display lab values if available
                        if record.get('lab_values'):
                            st.write("**Lab Values:**")
                            lab_values = record['lab_values']
                            
                            col_lab1, col_lab2 = st.columns(2)
                            with col_lab1:
                                if lab_values.get('hemoglobin'):
                                    st.write(f"• Hemoglobin: {lab_values['hemoglobin']} g/dL")
                                if lab_values.get('glucose'):
                                    st.write(f"• Glucose: {lab_values['glucose']} mg/dL")
                                if lab_values.get('cholesterol'):
                                    st.write(f"• Cholesterol: {lab_values['cholesterol']} mg/dL")
                            
                            with col_lab2:
                                if lab_values.get('white_blood_cells'):
                                    st.write(f"• WBC: {lab_values['white_blood_cells']} ×10³/μL")
                                if lab_values.get('blood_pressure'):
                                    st.write(f"• Blood Pressure: {lab_values['blood_pressure']} mmHg")
                    
                    with col2:
                        priority_colors = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
                        st.write(f"**Priority:** {priority_colors.get(record.get('priority', 'Low'), '🟢')} {record.get('priority', 'Low')}")
                        st.write(f"**Status:** {record.get('status', 'N/A')}")
                        
                        if record.get('file_name'):
                            st.write("📎 **File Attached**")
                            st.write(f"• {record['file_name']}")
        
        else:
            st.info(f"No medical records found for {patient['name']}.")

elif operation == "Lab Results":
    st.header("🧪 Laboratory Results")
    
    records = data_manager.get_medical_records()
    lab_records = [r for r in records if r.get('record_type') == 'Lab Result' and r.get('lab_values')]
    patients = data_manager.get_patients()
    patient_lookup = {p['id']: p['name'] for p in patients}
    
    if lab_records:
        st.subheader(f"📊 Lab Results Analysis ({len(lab_records)} records)")
        
        # Create DataFrame for analysis
        lab_data = []
        for record in lab_records:
            lab_values = record.get('lab_values', {})
            row = {
                'patient_name': patient_lookup.get(record['patient_id'], 'Unknown'),
                'date': record.get('date'),
                'hemoglobin': lab_values.get('hemoglobin'),
                'glucose': lab_values.get('glucose'),
                'cholesterol': lab_values.get('cholesterol'),
                'wbc': lab_values.get('white_blood_cells')
            }
            lab_data.append(row)
        
        df = pd.DataFrame(lab_data)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'hemoglobin' in df.columns and df['hemoglobin'].notna().any():
                fig = px.histogram(df.dropna(subset=['hemoglobin']), x='hemoglobin', 
                                 title="Hemoglobin Distribution")
                fig.add_vline(x=12, line_dash="dash", line_color="red", 
                            annotation_text="Normal Lower Limit")
                fig.add_vline(x=16, line_dash="dash", line_color="red", 
                            annotation_text="Normal Upper Limit")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'glucose' in df.columns and df['glucose'].notna().any():
                fig = px.histogram(df.dropna(subset=['glucose']), x='glucose', 
                                 title="Glucose Distribution")
                fig.add_vline(x=100, line_dash="dash", line_color="red", 
                            annotation_text="Normal Upper Limit")
                st.plotly_chart(fig, use_container_width=True)
        
        # Display lab records table
        st.subheader("📋 Lab Records Table")
        
        display_df = df[['patient_name', 'date', 'hemoglobin', 'glucose', 'cholesterol', 'wbc']].copy()
        display_df.columns = ['Patient', 'Date', 'Hemoglobin', 'Glucose', 'Cholesterol', 'WBC']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Abnormal results alert
        st.subheader("⚠️ Abnormal Results Alert")
        
        abnormal_results = []
        for _, row in df.iterrows():
            patient_name = row['patient_name']
            
            if pd.notna(row['hemoglobin']) and (row['hemoglobin'] < 12 or row['hemoglobin'] > 16):
                abnormal_results.append(f"🔴 {patient_name}: Hemoglobin {row['hemoglobin']} g/dL (Normal: 12-16)")
            
            if pd.notna(row['glucose']) and row['glucose'] > 100:
                abnormal_results.append(f"🟡 {patient_name}: Glucose {row['glucose']} mg/dL (Normal: <100)")
            
            if pd.notna(row['cholesterol']) and row['cholesterol'] > 200:
                abnormal_results.append(f"🟡 {patient_name}: Cholesterol {row['cholesterol']} mg/dL (Normal: <200)")
        
        if abnormal_results:
            for result in abnormal_results:
                st.warning(result)
        else:
            st.success("✅ All lab results within normal ranges!")
    
    else:
        st.info("No lab results with values found.")

elif operation == "Document Upload":
    st.header("📎 Document Management")
    
    patients = data_manager.get_patients()
    
    if not patients:
        st.warning("No patients available.")
    else:
        st.subheader("📤 Upload Medical Documents")
        
        with st.form("upload_document_form"):
            selected_patient = st.selectbox(
                "Select Patient",
                options=[p['id'] for p in patients],
                format_func=lambda x: next(p['name'] for p in patients if p['id'] == x)
            )
            
            document_type = st.selectbox(
                "Document Type",
                ["Lab Report", "X-Ray", "MRI Scan", "CT Scan", "Prescription", "Discharge Summary", "Other"]
            )
            
            document_title = st.text_input("Document Title", placeholder="e.g., Chest X-Ray Report")
            
            uploaded_files = st.file_uploader(
                "Upload Files",
                type=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'txt'],
                accept_multiple_files=True,
                help="You can upload multiple files at once"
            )
            
            notes = st.text_area("Notes", placeholder="Any additional notes about these documents...")
            
            submitted = st.form_submit_button("Upload Documents", type="primary")
            
            if submitted:
                if uploaded_files and document_title:
                    patient_name = next(p['name'] for p in patients if p['id'] == selected_patient)
                    
                    for file in uploaded_files:
                        # In a real application, you would save files to storage
                        # For demo purposes, we'll just create a record
                        record_data = {
                            'patient_id': selected_patient,
                            'record_type': 'Document',
                            'title': f"{document_title} - {file.name}",
                            'date': datetime.now().date().isoformat(),
                            'doctor': 'System',
                            'department': 'Records',
                            'description': f"Uploaded document: {file.name}",
                            'file_name': file.name,
                            'file_type': file.type,
                            'file_size': file.size,
                            'document_type': document_type,
                            'notes': notes,
                            'status': 'Active'
                        }
                        
                        data_manager.add_medical_record(record_data)
                    
                    st.success(f"Successfully uploaded {len(uploaded_files)} document(s) for {patient_name}!")
                    st.balloons()
                else:
                    st.error("Please provide a document title and select at least one file to upload.")
        
        # Display uploaded documents
        st.subheader("📁 Recently Uploaded Documents")
        
        records = data_manager.get_medical_records()
        document_records = [r for r in records if r.get('record_type') == 'Document' and r.get('file_name')]
        
        if document_records:
            # Show last 10 uploaded documents
            recent_docs = sorted(document_records, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
            
            for doc in recent_docs:
                patient_name = next((p['name'] for p in patients if p['id'] == doc['patient_id']), 'Unknown Patient')
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"📄 **{doc.get('title', 'Unknown Document')}**")
                        st.write(f"Patient: {patient_name}")
                    
                    with col2:
                        st.write(f"Type: {doc.get('document_type', 'Unknown')}")
                        st.write(f"Size: {doc.get('file_size', 0)/1024:.1f} KB")
                    
                    with col3:
                        uploaded_date = datetime.fromisoformat(doc.get('created_at', datetime.now().isoformat()))
                        st.write(f"Date: {uploaded_date.strftime('%Y-%m-%d')}")
                        st.write(f"Format: {doc.get('file_type', 'Unknown')}")
                    
                    with col4:
                        st.write("📎 Available")
                    
                    st.markdown("---")
        else:
            st.info("No documents uploaded yet.")

# Footer
st.markdown("---")
st.markdown("💡 **Tips:** Medical records provide a comprehensive view of patient health history. Use the timeline view to track patient progress over time.")
