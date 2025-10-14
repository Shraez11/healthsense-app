import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.db_manager import DatabaseManager
from utils.auth import init_auth, require_auth, is_authenticated

# Initialize database manager
@st.cache_resource
def get_data_manager():
    return DatabaseManager()

data_manager = get_data_manager()

st.set_page_config(page_title="Analytics - HealthSense", page_icon="📊", layout="wide")

# Initialize authentication
init_auth()
require_auth()

st.title("📊 Patient History Analytics & Health Trends")
st.markdown("---")

# Sidebar for patient selection
st.sidebar.header("Analytics Options")
patients = data_manager.get_patients()

if not patients:
    st.warning("No patients available for analytics.")
    st.stop()

selected_patient = st.sidebar.selectbox(
    "Select Patient",
    options=[p['id'] for p in patients],
    format_func=lambda x: next(p['name'] for p in patients if p['id'] == x)
)

patient = data_manager.get_patient_by_id(selected_patient)
patient_records = data_manager.get_medical_records_by_patient(selected_patient)
patient_prescriptions = data_manager.get_prescriptions_by_patient(selected_patient)
patient_appointments = data_manager.get_appointments_by_patient(selected_patient)
patient_predictions = data_manager.get_predictions_by_patient(selected_patient)

# Patient Overview Header
st.header(f"📋 Health Analytics for {patient['name']}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Age", patient.get('age', 'N/A'))

with col2:
    st.metric("Blood Group", patient.get('blood_group', 'N/A'))

with col3:
    st.metric("Total Records", len(patient_records))

with col4:
    active_prescriptions = len([p for p in patient_prescriptions if p['status'] == 'Active'])
    st.metric("Active Medications", active_prescriptions)

st.markdown("---")

# Health Timeline
st.subheader("📅 Health Timeline")

timeline_events = []

# Add appointments to timeline
for apt in patient_appointments:
    timeline_events.append({
        'date': apt['date'],
        'type': 'Appointment',
        'description': f"Visit with Dr. {apt['doctor']} - {apt['status']}",
        'category': 'Appointment'
    })

# Add medical records to timeline
for record in patient_records:
    timeline_events.append({
        'date': record['date'],
        'type': record['record_type'],
        'description': record['title'],
        'category': 'Medical Record'
    })

# Add prescriptions to timeline
for rx in patient_prescriptions:
    timeline_events.append({
        'date': rx['date_prescribed'],
        'type': 'Prescription',
        'description': f"{rx['medication_name']} - {rx['status']}",
        'category': 'Prescription'
    })

if timeline_events:
    timeline_df = pd.DataFrame(timeline_events)
    timeline_df['date'] = pd.to_datetime(timeline_df['date'])
    timeline_df = timeline_df.sort_values('date', ascending=False)
    
    # Display timeline
    fig = px.timeline(
        timeline_df.head(20),
        x_start='date',
        x_end='date',
        y='type',
        color='category',
        hover_data=['description'],
        title="Recent Health Events Timeline (Last 20 Events)"
    )
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No timeline events available for this patient.")

st.markdown("---")

# Lab Values Trend Analysis
st.subheader("🧪 Lab Results Trend Analysis")

lab_records = [r for r in patient_records if r.get('record_type') == 'Lab Result' and r.get('lab_values')]

if lab_records:
    # Extract lab values over time
    lab_data = []
    for record in lab_records:
        lab_values = record.get('lab_values', {})
        record_date = record['date']
        
        for key, value in lab_values.items():
            if isinstance(value, (int, float)):
                lab_data.append({
                    'date': record_date,
                    'test': key.replace('_', ' ').title(),
                    'value': value
                })
    
    if lab_data:
        lab_df = pd.DataFrame(lab_data)
        lab_df['date'] = pd.to_datetime(lab_df['date'])
        
        # Show trends for each test type
        available_tests = lab_df['test'].unique()
        
        col1, col2 = st.columns(2)
        
        # Hemoglobin trend
        if 'Hemoglobin' in available_tests:
            with col1:
                hb_data = lab_df[lab_df['test'] == 'Hemoglobin']
                fig = px.line(hb_data, x='date', y='value', title='Hemoglobin Levels Over Time')
                fig.add_hline(y=12, line_dash="dash", line_color="red", annotation_text="Normal Lower Limit")
                fig.add_hline(y=16, line_dash="dash", line_color="red", annotation_text="Normal Upper Limit")
                fig.update_yaxes(title="Hemoglobin (g/dL)")
                st.plotly_chart(fig, use_container_width=True)
        
        # Glucose trend
        if 'Glucose' in available_tests:
            with col2:
                glucose_data = lab_df[lab_df['test'] == 'Glucose']
                fig = px.line(glucose_data, x='date', y='value', title='Glucose Levels Over Time')
                fig.add_hline(y=100, line_dash="dash", line_color="orange", annotation_text="Normal Upper Limit")
                fig.update_yaxes(title="Glucose (mg/dL)")
                st.plotly_chart(fig, use_container_width=True)
        
        # Cholesterol trend
        if 'Cholesterol' in available_tests:
            cholesterol_data = lab_df[lab_df['test'] == 'Cholesterol']
            fig = px.line(cholesterol_data, x='date', y='value', title='Cholesterol Levels Over Time')
            fig.add_hline(y=200, line_dash="dash", line_color="orange", annotation_text="Normal Upper Limit")
            fig.update_yaxes(title="Cholesterol (mg/dL)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric lab values available for trend analysis.")
else:
    st.info("No lab results available for this patient.")

st.markdown("---")

# Medication History
st.subheader("💊 Medication History & Analysis")

if patient_prescriptions:
    # Medication timeline
    med_data = []
    for rx in patient_prescriptions:
        med_data.append({
            'medication': rx['medication_name'],
            'prescribed_date': rx['date_prescribed'],
            'status': rx['status'],
            'dosage': rx['dosage']
        })
    
    med_df = pd.DataFrame(med_data)
    med_df['prescribed_date'] = pd.to_datetime(med_df['prescribed_date'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Medication frequency
        med_counts = med_df['medication'].value_counts().head(10)
        fig = px.bar(x=med_counts.values, y=med_counts.index, orientation='h',
                    title="Most Prescribed Medications")
        fig.update_yaxes(title="Medication")
        fig.update_xaxes(title="Number of Prescriptions")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Status distribution
        status_counts = med_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index,
                    title="Prescription Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Prescriptions over time
    med_by_month = med_df.groupby(med_df['prescribed_date'].dt.to_period('M')).size()
    fig = px.line(x=med_by_month.index.astype(str), y=med_by_month.values,
                 title="Prescriptions Over Time")
    fig.update_xaxes(title="Month")
    fig.update_yaxes(title="Number of Prescriptions")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No prescription history available for this patient.")

st.markdown("---")

# Disease Prediction History
st.subheader("🔬 Disease Prediction History & Patterns")

if patient_predictions:
    pred_data = []
    for pred in patient_predictions:
        pred_data.append({
            'date': pred['prediction_date'],
            'disease': pred['primary_prediction'],
            'confidence': pred['confidence'],
            'symptom_count': pred['symptom_count']
        })
    
    pred_df = pd.DataFrame(pred_data)
    pred_df['date'] = pd.to_datetime(pred_df['date'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Prediction frequency
        disease_counts = pred_df['disease'].value_counts()
        fig = px.bar(x=disease_counts.values, y=disease_counts.index, orientation='h',
                    title="Predicted Conditions Frequency")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Confidence distribution
        fig = px.histogram(pred_df, x='confidence', nbins=20,
                          title="Prediction Confidence Distribution")
        fig.add_vline(x=0.8, line_dash="dash", line_color="green",
                     annotation_text="High Confidence Threshold")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No disease prediction history available for this patient.")

st.markdown("---")

# Health Risk Score (Predictive Analytics)
st.subheader("⚠️ Health Risk Assessment")

risk_factors = []
risk_score = 0

# Age-based risk
age = patient.get('age', 0)
if isinstance(age, (int, float)):
    if age > 65:
        risk_factors.append("Senior age group (>65)")
        risk_score += 2
    elif age > 50:
        risk_factors.append("Middle age group (50-65)")
        risk_score += 1

# Medication complexity
active_meds = len([p for p in patient_prescriptions if p['status'] == 'Active'])
if active_meds > 5:
    risk_factors.append(f"High medication count ({active_meds} active)")
    risk_score += 2
elif active_meds > 3:
    risk_factors.append(f"Moderate medication count ({active_meds} active)")
    risk_score += 1

# Recent lab abnormalities
abnormal_labs = 0
for record in lab_records[-3:]:  # Check last 3 lab results
    lab_values = record.get('lab_values', {})
    if lab_values.get('hemoglobin'):
        if lab_values['hemoglobin'] < 12 or lab_values['hemoglobin'] > 16:
            abnormal_labs += 1
    if lab_values.get('glucose'):
        if lab_values['glucose'] > 100:
            abnormal_labs += 1

if abnormal_labs > 2:
    risk_factors.append("Multiple abnormal lab results")
    risk_score += 2
elif abnormal_labs > 0:
    risk_factors.append("Some abnormal lab results")
    risk_score += 1

# Frequent visits
recent_appointments = len([a for a in patient_appointments 
                          if datetime.fromisoformat(a['date']) > datetime.now() - timedelta(days=90)])
if recent_appointments > 5:
    risk_factors.append(f"Frequent visits ({recent_appointments} in last 90 days)")
    risk_score += 1

# Display risk assessment
col1, col2 = st.columns([1, 2])

with col1:
    # Risk gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Score"},
        gauge={
            'axis': {'range': [None, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3], 'color': "lightgreen"},
                {'range': [3, 6], 'color': "yellow"},
                {'range': [6, 10], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 7
            }
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    if risk_score <= 3:
        st.success("🟢 Low Risk - Patient appears to be in stable condition")
    elif risk_score <= 6:
        st.warning("🟡 Moderate Risk - Consider closer monitoring")
    else:
        st.error("🔴 High Risk - Immediate attention recommended")
    
    if risk_factors:
        st.write("**Risk Factors Identified:**")
        for factor in risk_factors:
            st.write(f"• {factor}")
    else:
        st.write("No significant risk factors identified.")

# Recommendations based on analytics
st.markdown("---")
st.subheader("💡 Personalized Recommendations")

recommendations = []

if active_meds > 5:
    recommendations.append("🔍 Review medication interactions with pharmacist")

if abnormal_labs > 0:
    recommendations.append("🧪 Schedule follow-up lab tests to monitor abnormal values")

if risk_score > 6:
    recommendations.append("⚠️ Schedule comprehensive health evaluation")

if len(patient_appointments) == 0:
    recommendations.append("📅 Schedule regular check-up appointment")

if patient.get('medical_history') and 'diabetes' in patient['medical_history'].lower():
    recommendations.append("🩸 Regular blood glucose monitoring recommended")

if recommendations:
    for rec in recommendations:
        st.info(rec)
else:
    st.success("✅ No urgent recommendations at this time. Continue regular monitoring.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>📊 Analytics generated on: {}</p>
    <p><em>These analytics are for informational purposes and should be reviewed by healthcare professionals.</em></p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)
