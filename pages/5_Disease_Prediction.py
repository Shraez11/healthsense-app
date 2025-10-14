import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.db_manager import DatabaseManager
from utils.auth import init_auth, require_auth, is_authenticated
from utils.ai_models import get_disease_predictor

# Initialize database manager and AI model
@st.cache_resource
def get_data_manager():
    return DatabaseManager()

data_manager = get_data_manager()
disease_predictor = get_disease_predictor()

st.set_page_config(page_title="Disease Prediction - HealthSense", page_icon="🔬", layout="wide")

# Initialize authentication
init_auth()
require_auth()

st.title("🔬 AI-Powered Disease Prediction System")
st.markdown("---")

# Sidebar for operations
st.sidebar.header("Prediction Operations")
operation = st.sidebar.selectbox(
    "Select Operation",
    ["Symptom Analysis", "Patient Prediction", "Prediction History", "Model Analytics"]
)

if operation == "Symptom Analysis":
    st.header("🩺 Symptom-Based Disease Prediction")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Select Symptoms")
        st.write("Check all symptoms that are currently present:")
        
        # Get available symptoms from the AI model
        available_symptoms = disease_predictor.get_available_symptoms()
        
        # Organize symptoms into categories for better UX
        symptom_categories = {
            "General Symptoms": ['fever', 'fatigue', 'headache', 'dizziness', 'confusion'],
            "Respiratory": ['cough', 'shortness_of_breath', 'sore_throat', 'runny_nose'],
            "Gastrointestinal": ['nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 'loss_of_appetite'],
            "Pain & Body": ['body_ache', 'chest_pain', 'joint_pain', 'muscle_weakness'],
            "Other": []
        }
        
        # Categorize symptoms
        for symptom in available_symptoms:
            categorized = False
            for category, symptoms_list in symptom_categories.items():
                if symptom in symptoms_list:
                    categorized = True
                    break
            if not categorized:
                symptom_categories["Other"].append(symptom)
        
        selected_symptoms = {}
        
        for category, symptoms in symptom_categories.items():
            if symptoms:  # Only show categories that have symptoms
                st.write(f"**{category}:**")
                cols = st.columns(2)
                
                for i, symptom in enumerate(symptoms):
                    with cols[i % 2]:
                        selected_symptoms[symptom] = st.checkbox(
                            symptom.replace('_', ' ').title(),
                            key=f"symptom_{symptom}"
                        )
                
                st.markdown("---")
        
        # Count selected symptoms
        selected_count = sum(selected_symptoms.values())
        
        if selected_count > 0:
            st.info(f"📊 {selected_count} symptoms selected")
            
            if st.button("🔬 Analyze Symptoms", type="primary"):
                with st.spinner("Analyzing symptoms using AI model..."):
                    # Get prediction from AI model
                    prediction_result = disease_predictor.predict_disease(selected_symptoms)
                    
                    if "error" not in prediction_result:
                        # Store prediction result in session state for display
                        st.session_state['latest_prediction'] = prediction_result
                        st.session_state['latest_symptoms'] = selected_symptoms
                        st.success("✅ Analysis complete! See results on the right.")
                        st.rerun()
                    else:
                        st.error(f"❌ Analysis failed: {prediction_result['error']}")
        else:
            st.warning("⚠️ Please select at least one symptom to analyze.")
    
    with col2:
        st.subheader("🎯 Prediction Results")
        
        if 'latest_prediction' in st.session_state:
            prediction = st.session_state['latest_prediction']
            symptoms = st.session_state['latest_symptoms']
            
            # Primary prediction
            st.metric(
                "Primary Prediction", 
                prediction['primary_prediction'],
                f"{prediction['confidence']:.1%} confidence"
            )
            
            # Confidence meter
            confidence_fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = prediction['confidence'] * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Confidence Level"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            confidence_fig.update_layout(height=200)
            st.plotly_chart(confidence_fig, use_container_width=True)
            
            # Top predictions
            st.subheader("📊 Top Predictions")
            
            for i, pred in enumerate(prediction['top_predictions'][:3]):
                percentage = pred['probability'] * 100
                st.progress(pred['probability'], text=f"{i+1}. {pred['disease']} ({percentage:.1f}%)")
            
            # Recommendations based on confidence
            st.subheader("💡 Recommendations")
            
            confidence = prediction['confidence']
            if confidence >= 0.8:
                st.success("🟢 **High Confidence Prediction**")
                st.write("• Consider consulting a healthcare professional")
                st.write("• Monitor symptoms closely")
                st.write("• Follow standard care protocols")
            elif confidence >= 0.6:
                st.warning("🟡 **Moderate Confidence Prediction**")
                st.write("• Multiple conditions possible")
                st.write("• Seek professional medical advice")
                st.write("• Additional tests may be needed")
            else:
                st.error("🔴 **Low Confidence Prediction**")
                st.write("• Symptoms are not clearly indicative")
                st.write("• Consult a healthcare professional immediately")
                st.write("• Consider comprehensive examination")
            
            # Important disclaimer
            st.warning("⚠️ **Medical Disclaimer**: This AI prediction is for informational purposes only and should not replace professional medical diagnosis or treatment. Always consult qualified healthcare professionals for medical advice.")
            
            # Save prediction option
            st.subheader("💾 Save Prediction")
            
            patients = data_manager.get_patients()
            if patients:
                save_to_patient = st.selectbox(
                    "Save to Patient Record",
                    ["None"] + [p['name'] for p in patients],
                    key="save_prediction_patient"
                )
                
                if save_to_patient != "None" and st.button("Save Prediction", type="secondary"):
                    patient_id = next(p['id'] for p in patients if p['name'] == save_to_patient)
                    
                    # Prepare prediction data for storage
                    prediction_data = {
                        'patient_id': patient_id,
                        'symptoms': [symptom for symptom, selected in symptoms.items() if selected],
                        'primary_prediction': prediction['primary_prediction'],
                        'confidence': prediction['confidence'],
                        'all_predictions': prediction['top_predictions'],
                        'symptom_count': prediction['total_symptoms'],
                        'prediction_date': datetime.now().isoformat()
                    }
                    
                    pred_id = data_manager.add_disease_prediction(prediction_data)
                    st.success(f"✅ Prediction saved to {save_to_patient}'s record!")
        else:
            st.info("🔍 Select symptoms and click 'Analyze Symptoms' to see prediction results here.")

elif operation == "Patient Prediction":
    st.header("👤 Patient-Specific Disease Prediction")
    
    patients = data_manager.get_patients()
    
    if not patients:
        st.warning("No patients available. Please add patients first.")
    else:
        selected_patient = st.selectbox(
            "Select Patient",
            options=[p['id'] for p in patients],
            format_func=lambda x: next(p['name'] for p in patients if p['id'] == x)
        )
        
        patient = data_manager.get_patient_by_id(selected_patient)
        
        # Display patient context
        st.subheader(f"👤 Patient: {patient['name']}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Age", patient.get('age', 'N/A'))
        with col2:
            st.metric("Gender", patient.get('gender', 'N/A'))
        with col3:
            st.metric("Blood Group", patient.get('blood_group', 'N/A'))
        with col4:
            existing_predictions = len(data_manager.get_predictions_by_patient(selected_patient))
            st.metric("Previous Predictions", existing_predictions)
        
        # Patient context information
        if patient.get('medical_history') or patient.get('current_medications'):
            with st.expander("📋 Patient Medical Context"):
                if patient.get('medical_history'):
                    st.write(f"**Medical History:** {patient['medical_history']}")
                
                if patient.get('current_medications'):
                    st.write(f"**Current Medications:** {patient['current_medications']}")
        
        # Symptom selection for this patient
        st.subheader("🩺 Current Symptoms Assessment")
        
        available_symptoms = disease_predictor.get_available_symptoms()
        selected_symptoms = {}
        
        # Create symptom selection interface
        cols = st.columns(3)
        
        for i, symptom in enumerate(available_symptoms):
            with cols[i % 3]:
                selected_symptoms[symptom] = st.checkbox(
                    symptom.replace('_', ' ').title(),
                    key=f"patient_symptom_{symptom}"
                )
        
        # Severity assessment
        st.subheader("📈 Symptom Severity")
        severity_level = st.selectbox(
            "Overall Symptom Severity",
            ["Mild", "Moderate", "Severe", "Critical"]
        )
        
        # Duration assessment
        symptom_duration = st.selectbox(
            "Symptom Duration",
            ["Less than 24 hours", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"]
        )
        
        # Additional notes
        additional_notes = st.text_area(
            "Additional Notes",
            placeholder="Any additional information about symptoms, triggers, or concerns..."
        )
        
        selected_count = sum(selected_symptoms.values())
        
        if selected_count > 0:
            st.info(f"📊 {selected_count} symptoms selected with {severity_level.lower()} severity")
            
            if st.button("🔬 Generate Patient Prediction", type="primary"):
                with st.spinner("Analyzing patient symptoms..."):
                    # Get prediction from AI model
                    prediction_result = disease_predictor.predict_disease(selected_symptoms)
                    
                    if "error" not in prediction_result:
                        # Display results
                        st.success("✅ Patient analysis complete!")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🎯 Prediction Results")
                            
                            # Primary prediction with patient context
                            st.metric(
                                "Primary Prediction", 
                                prediction_result['primary_prediction'],
                                f"{prediction_result['confidence']:.1%} confidence"
                            )
                            
                            # Top predictions chart
                            pred_df = pd.DataFrame(prediction_result['top_predictions'])
                            fig = px.bar(pred_df, x='probability', y='disease',
                                       orientation='h', title="Prediction Probabilities")
                            fig.update_traces(marker_color='lightblue')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.subheader("📋 Assessment Details")
                            st.write(f"**Patient:** {patient['name']}")
                            st.write(f"**Age:** {patient.get('age', 'N/A')}")
                            st.write(f"**Severity:** {severity_level}")
                            st.write(f"**Duration:** {symptom_duration}")
                            st.write(f"**Symptoms:** {selected_count}")
                            
                            # Patient-specific recommendations
                            st.subheader("🔍 Recommendations")
                            
                            age = patient.get('age', 0)
                            if isinstance(age, (int, float)) and age > 65:
                                st.warning("👴 **Senior Patient Alert**: Consider age-related complications")
                            
                            if patient.get('medical_history'):
                                st.info("📋 **Medical History**: Review existing conditions for interactions")
                            
                            if patient.get('current_medications'):
                                st.info("💊 **Current Medications**: Check for drug-disease interactions")
                        
                        # Save prediction with patient context
                        if st.button("💾 Save Patient Prediction", type="secondary"):
                            prediction_data = {
                                'patient_id': selected_patient,
                                'symptoms': [symptom for symptom, selected in selected_symptoms.items() if selected],
                                'primary_prediction': prediction_result['primary_prediction'],
                                'confidence': prediction_result['confidence'],
                                'all_predictions': prediction_result['top_predictions'],
                                'symptom_count': prediction_result['total_symptoms'],
                                'severity': severity_level,
                                'duration': symptom_duration,
                                'additional_notes': additional_notes,
                                'prediction_date': datetime.now().isoformat()
                            }
                            
                            pred_id = data_manager.add_disease_prediction(prediction_data)
                            st.success(f"✅ Prediction saved to {patient['name']}'s record!")
                            st.balloons()
                    
                    else:
                        st.error(f"❌ Analysis failed: {prediction_result['error']}")
        else:
            st.warning("⚠️ Please select at least one symptom for the patient.")

elif operation == "Prediction History":
    st.header("📚 Disease Prediction History")
    
    predictions = data_manager.get_disease_predictions()
    patients = data_manager.get_patients()
    patient_lookup = {p['id']: p['name'] for p in patients}
    
    if predictions:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Predictions", len(predictions))
        
        with col2:
            unique_patients = len(set([p['patient_id'] for p in predictions]))
            st.metric("Patients Analyzed", unique_patients)
        
        with col3:
            high_confidence = len([p for p in predictions if p.get('confidence', 0) >= 0.8])
            st.metric("High Confidence", high_confidence)
        
        with col4:
            recent_predictions = len([p for p in predictions if 
                datetime.fromisoformat(p.get('prediction_date', '2000-01-01')) > datetime.now() - pd.Timedelta(days=7)])
            st.metric("This Week", recent_predictions)
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            patient_filter = st.selectbox(
                "Filter by Patient",
                ["All"] + [p['name'] for p in patients]
            )
        
        with col2:
            confidence_filter = st.selectbox(
                "Filter by Confidence",
                ["All", "High (≥80%)", "Medium (60-80%)", "Low (<60%)"]
            )
        
        # Apply filters
        filtered_predictions = predictions
        
        if patient_filter != "All":
            patient_id = next(p['id'] for p in patients if p['name'] == patient_filter)
            filtered_predictions = [p for p in filtered_predictions if p['patient_id'] == patient_id]
        
        if confidence_filter != "All":
            if confidence_filter == "High (≥80%)":
                filtered_predictions = [p for p in filtered_predictions if p.get('confidence', 0) >= 0.8]
            elif confidence_filter == "Medium (60-80%)":
                filtered_predictions = [p for p in filtered_predictions if 0.6 <= p.get('confidence', 0) < 0.8]
            elif confidence_filter == "Low (<60%)":
                filtered_predictions = [p for p in filtered_predictions if p.get('confidence', 0) < 0.6]
        
        st.subheader(f"📊 Showing {len(filtered_predictions)} predictions")
        
        # Sort by date (newest first)
        sorted_predictions = sorted(filtered_predictions, 
                                   key=lambda x: x.get('prediction_date', '2000-01-01'), 
                                   reverse=True)
        
        # Display predictions
        for prediction in sorted_predictions:
            patient_name = patient_lookup.get(prediction['patient_id'], 'Unknown Patient')
            pred_date = datetime.fromisoformat(prediction.get('prediction_date', '2000-01-01')).strftime('%B %d, %Y %I:%M %p')
            
            with st.expander(f"🔬 {prediction.get('primary_prediction', 'Unknown')} - {patient_name} ({pred_date})"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Patient:** {patient_name}")
                    st.write(f"**Primary Prediction:** {prediction.get('primary_prediction', 'N/A')}")
                    st.write(f"**Confidence:** {prediction.get('confidence', 0):.1%}")
                    st.write(f"**Symptom Count:** {prediction.get('symptom_count', 0)}")
                    
                    if prediction.get('severity'):
                        st.write(f"**Severity:** {prediction['severity']}")
                    
                    if prediction.get('duration'):
                        st.write(f"**Duration:** {prediction['duration']}")
                
                with col2:
                    st.write(f"**Date:** {pred_date}")
                    
                    if prediction.get('symptoms'):
                        st.write("**Symptoms:**")
                        symptoms_text = ", ".join([s.replace('_', ' ').title() for s in prediction['symptoms']])
                        st.write(symptoms_text)
                    
                    if prediction.get('additional_notes'):
                        st.write(f"**Notes:** {prediction['additional_notes']}")
                
                with col3:
                    confidence = prediction.get('confidence', 0)
                    if confidence >= 0.8:
                        st.success("🟢 High Confidence")
                    elif confidence >= 0.6:
                        st.warning("🟡 Medium Confidence")
                    else:
                        st.error("🔴 Low Confidence")
                
                # Show all predictions if available
                if prediction.get('all_predictions'):
                    st.write("**All Predictions:**")
                    pred_df = pd.DataFrame(prediction['all_predictions'])
                    pred_df['probability_pct'] = pred_df['probability'] * 100
                    st.dataframe(pred_df[['disease', 'probability_pct']], use_container_width=True)
    
    else:
        st.info("No disease predictions found. Start by analyzing symptoms in the Symptom Analysis section.")

elif operation == "Model Analytics":
    st.header("📈 Disease Prediction Model Analytics")
    
    predictions = data_manager.get_disease_predictions()
    patients = data_manager.get_patients()
    
    if predictions:
        # Prediction trends
        st.subheader("📊 Prediction Trends")
        
        # Create DataFrame for analysis
        pred_data = []
        for pred in predictions:
            pred_date = datetime.fromisoformat(pred.get('prediction_date', '2000-01-01'))
            pred_data.append({
                'date': pred_date,
                'prediction': pred.get('primary_prediction', 'Unknown'),
                'confidence': pred.get('confidence', 0),
                'symptom_count': pred.get('symptom_count', 0),
                'patient_id': pred['patient_id']
            })
        
        df = pd.DataFrame(pred_data)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Most common predictions
            prediction_counts = df['prediction'].value_counts().head(10)
            
            fig = px.bar(
                x=prediction_counts.values, 
                y=prediction_counts.index,
                orientation='h',
                title="Most Common Predictions",
                labels={'x': 'Count', 'y': 'Disease'}
            )
            fig.update_traces(marker_color='lightcoral')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Confidence distribution
            fig = px.histogram(df, x='confidence', nbins=20, 
                             title="Confidence Level Distribution")
            fig.update_traces(marker_color='lightblue')
            fig.add_vline(x=0.8, line_dash="dash", line_color="green", 
                        annotation_text="High Confidence Threshold")
            fig.add_vline(x=0.6, line_dash="dash", line_color="orange", 
                        annotation_text="Medium Confidence Threshold")
            st.plotly_chart(fig, use_container_width=True)
        
        # Predictions over time
        st.subheader("📅 Predictions Timeline")
        
        daily_counts = df.groupby(df['date'].dt.date).size()
        
        fig = px.line(x=daily_counts.index, y=daily_counts.values,
                     title="Daily Prediction Count",
                     labels={'x': 'Date', 'y': 'Predictions'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Model performance metrics
        st.subheader("🎯 Model Performance Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_confidence = df['confidence'].mean()
            st.metric("Average Confidence", f"{avg_confidence:.1%}")
        
        with col2:
            avg_symptoms = df['symptom_count'].mean()
            st.metric("Average Symptoms", f"{avg_symptoms:.1f}")
        
        with col3:
            high_conf_rate = (df['confidence'] >= 0.8).mean()
            st.metric("High Confidence Rate", f"{high_conf_rate:.1%}")
        
        # Symptom analysis
        st.subheader("🔍 Symptom Analysis")
        
        # Get symptom importance from the model
        if predictions:
            latest_pred = predictions[-1]
            if latest_pred.get('symptoms'):
                symptoms_dict = {symptom: True for symptom in latest_pred['symptoms']}
                importance = disease_predictor.get_symptom_importance(symptoms_dict)
                
                if importance:
                    importance_df = pd.DataFrame(list(importance.items()), 
                                               columns=['Symptom', 'Importance'])
                    importance_df = importance_df.sort_values('Importance', ascending=True)
                    
                    fig = px.bar(importance_df, x='Importance', y='Symptom',
                               orientation='h', title="Symptom Importance in Latest Prediction")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Performance recommendations
        st.subheader("💡 Model Insights & Recommendations")
        
        high_conf_predictions = df[df['confidence'] >= 0.8]
        low_conf_predictions = df[df['confidence'] < 0.6]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ **High Confidence Predictions**")
            st.write(f"• {len(high_conf_predictions)} predictions with ≥80% confidence")
            if len(high_conf_predictions) > 0:
                top_high_conf = high_conf_predictions['prediction'].value_counts().head(3)
                st.write("• Most confident predictions:")
                for disease, count in top_high_conf.items():
                    st.write(f"  - {disease}: {count} cases")
        
        with col2:
            st.warning("⚠️ **Low Confidence Predictions**")
            st.write(f"• {len(low_conf_predictions)} predictions with <60% confidence")
            if len(low_conf_predictions) > 0:
                st.write("• May require additional symptoms or medical consultation")
                avg_symptoms_low = low_conf_predictions['symptom_count'].mean()
                st.write(f"• Average symptoms in low confidence: {avg_symptoms_low:.1f}")
        
        # Model accuracy disclaimer
        st.info("📝 **Note**: This AI model is trained on synthetic data for demonstration purposes. In a production environment, it would be trained on validated medical datasets and regularly updated with new medical research.")
    
    else:
        st.info("No prediction data available for analytics. Generate some predictions first!")

# Footer
st.markdown("---")
st.markdown("💡 **Tips:** Disease prediction is most accurate with multiple symptoms. Always consult healthcare professionals for proper diagnosis and treatment.")

