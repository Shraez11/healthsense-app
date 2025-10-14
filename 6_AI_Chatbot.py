import streamlit as st
from datetime import datetime
import json
from utils.db_manager import DatabaseManager
from utils.auth import init_auth, require_auth, is_authenticated
from utils.openai_client import HealthcareAI

# Initialize database manager and AI client
@st.cache_resource
def get_data_manager():
    return DatabaseManager()

@st.cache_resource
def get_healthcare_ai():
    return HealthcareAI()

data_manager = get_data_manager()
healthcare_ai = get_healthcare_ai()

st.set_page_config(page_title="AI Chatbot - HealthSense", page_icon="🤖", layout="wide")

# Initialize authentication
init_auth()
require_auth()

st.title("🤖 HealthSense AI Assistant")
st.markdown("---")

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'selected_patient_context' not in st.session_state:
    st.session_state.selected_patient_context = None

# Sidebar for chat controls
st.sidebar.header("AI Assistant Controls")

# Patient context selection
patients = data_manager.get_patients()
if patients:
    st.sidebar.subheader("👤 Patient Context")
    
    patient_options = ["None"] + [f"{p['name']} (Age: {p.get('age', 'N/A')})" for p in patients]
    selected_patient_display = st.sidebar.selectbox(
        "Select Patient for Context",
        patient_options,
        key="patient_context_select"
    )
    
    if selected_patient_display != "None":
        # Extract patient name from display string
        patient_name = selected_patient_display.split(" (Age:")[0]
        selected_patient = next(p for p in patients if p['name'] == patient_name)
        st.session_state.selected_patient_context = selected_patient
        
        # Show selected patient info
        st.sidebar.success(f"✅ Context: {selected_patient['name']}")
        st.sidebar.write(f"Age: {selected_patient.get('age', 'N/A')}")
        st.sidebar.write(f"Gender: {selected_patient.get('gender', 'N/A')}")
        
        if selected_patient.get('medical_history'):
            with st.sidebar.expander("Medical History"):
                st.write(selected_patient['medical_history'])
        
        if selected_patient.get('current_medications'):
            with st.sidebar.expander("Current Medications"):
                st.write(selected_patient['current_medications'])
    else:
        st.session_state.selected_patient_context = None

# Chat controls
st.sidebar.markdown("---")
st.sidebar.subheader("💬 Chat Controls")

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

# Quick actions
st.sidebar.subheader("⚡ Quick Actions")

if st.sidebar.button("💊 Medication Interactions"):
    if st.session_state.selected_patient_context:
        patient = st.session_state.selected_patient_context
        if patient.get('current_medications'):
            quick_query = f"Can you analyze potential interactions for these medications: {patient['current_medications']}?"
            st.session_state.chat_history.append({
                "role": "user",
                "content": quick_query,
                "timestamp": datetime.now().isoformat()
            })
            st.rerun()
        else:
            st.sidebar.warning("No medications listed for selected patient")
    else:
        st.sidebar.warning("Please select a patient first")

if st.sidebar.button("🩺 Health Tips"):
    quick_query = "Can you provide some general health and wellness tips?"
    st.session_state.chat_history.append({
        "role": "user",
        "content": quick_query,
        "timestamp": datetime.now().isoformat()
    })
    st.rerun()

if st.sidebar.button("🚨 Emergency Symptoms"):
    quick_query = "What are the warning signs that require immediate medical attention?"
    st.session_state.chat_history.append({
        "role": "user",
        "content": quick_query,
        "timestamp": datetime.now().isoformat()
    })
    st.rerun()

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Chat with AI Assistant")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            # Welcome message
            st.markdown("""
            <div style='padding: 20px; background-color: #f0f7ff; border-left: 4px solid #2E86AB; border-radius: 5px; margin: 10px 0;'>
                <h4>👋 Welcome to HealthSense AI Assistant!</h4>
                <p>I'm here to help you with healthcare-related questions. I can assist with:</p>
                <ul>
                    <li>🩺 General health information and advice</li>
                    <li>💊 Medication information and interactions</li>
                    <li>🔍 Symptom analysis and guidance</li>
                    <li>📋 Medical report interpretation</li>
                    <li>💡 Health tips and wellness advice</li>
                </ul>
                <p><strong>Important:</strong> I provide information for educational purposes only. Always consult healthcare professionals for medical decisions.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.chat_history:
            timestamp = datetime.fromisoformat(message['timestamp']).strftime('%H:%M')
            
            if message['role'] == 'user':
                st.markdown(f"""
                <div style='padding: 10px; margin: 10px 0; background-color: #e3f2fd; border-radius: 10px; margin-left: 50px;'>
                    <div style='font-size: 0.8em; color: #666; margin-bottom: 5px;'>You - {timestamp}</div>
                    <div>{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                st.markdown(f"""
                <div style='padding: 10px; margin: 10px 0; background-color: #f5f5f5; border-radius: 10px; margin-right: 50px;'>
                    <div style='font-size: 0.8em; color: #666; margin-bottom: 5px;'>🤖 AI Assistant - {timestamp}</div>
                    <div>{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Ask me anything about health and medical topics:",
            placeholder="e.g., What are the symptoms of diabetes? or Can you explain my blood test results?",
            height=100
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            submitted = st.form_submit_button("Send Message", type="primary")
        
        with col_btn2:
            analyze_symptoms = st.form_submit_button("🩺 Analyze Symptoms")
        
        if submitted and user_input.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get AI response
            with st.spinner("AI Assistant is thinking..."):
                patient_context = st.session_state.selected_patient_context
                
                try:
                    ai_response = healthcare_ai.get_medical_advice(user_input, patient_context)
                    
                    # Add AI response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    error_response = f"I apologize, but I'm having trouble processing your request right now. Please try again later. Error: {str(e)}"
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_response,
                        "timestamp": datetime.now().isoformat()
                    })
            
            st.rerun()
        
        elif analyze_symptoms and user_input.strip():
            # Special handling for symptom analysis
            st.session_state.chat_history.append({
                "role": "user",
                "content": f"🩺 SYMPTOM ANALYSIS REQUEST: {user_input}",
                "timestamp": datetime.now().isoformat()
            })
            
            with st.spinner("Analyzing symptoms..."):
                try:
                    # Extract symptoms from text (simplified approach)
                    symptoms_text = user_input.lower()
                    common_symptoms = [
                        'fever', 'cough', 'fatigue', 'headache', 'nausea', 'vomiting',
                        'diarrhea', 'shortness of breath', 'chest pain', 'dizziness'
                    ]
                    
                    detected_symptoms = [s for s in common_symptoms if s in symptoms_text]
                    
                    if detected_symptoms:
                        patient_info = st.session_state.selected_patient_context
                        analysis_result = healthcare_ai.analyze_symptoms(detected_symptoms, patient_info)
                        
                        # Format the response
                        if 'error' not in analysis_result:
                            response = f"""
🔍 **Symptom Analysis Results:**

**Detected Symptoms:** {', '.join(detected_symptoms)}

**Possible Conditions:** {', '.join(analysis_result.get('conditions', ['Unable to determine']))}

**Urgency Level:** {analysis_result.get('urgency', 'Medium')}

**Recommendations:**
{chr(10).join(['• ' + rec for rec in analysis_result.get('recommendations', ['Consult healthcare provider'])])}

**Warning Signs to Watch For:**
{chr(10).join(['• ' + sign for sign in analysis_result.get('warning_signs', ['Any worsening symptoms'])])}

⚠️ **Important:** This analysis is for informational purposes only. Please consult with a healthcare professional for proper diagnosis and treatment.
                            """
                        else:
                            response = f"I had trouble analyzing the symptoms. {analysis_result.get('error', 'Please try rephrasing your symptoms or consult a healthcare provider.')}"
                    else:
                        response = "I couldn't detect specific symptoms in your message. Please list your symptoms more clearly (e.g., 'I have fever, cough, and headache')."
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    error_response = f"I'm having trouble analyzing symptoms right now. Please try again later or consult a healthcare provider. Error: {str(e)}"
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_response,
                        "timestamp": datetime.now().isoformat()
                    })
            
            st.rerun()

with col2:
    st.subheader("🛠️ AI Assistant Features")
    
    # Feature cards
    st.markdown("""
    <div style='padding: 15px; background-color: #e8f5e8; border-radius: 10px; margin: 10px 0;'>
        <h4>🩺 Medical Consultation</h4>
        <p>Get information about symptoms, conditions, and general health advice.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='padding: 15px; background-color: #fff3e0; border-radius: 10px; margin: 10px 0;'>
        <h4>💊 Medication Help</h4>
        <p>Check drug interactions, side effects, and medication information.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='padding: 15px; background-color: #f3e5f5; border-radius: 10px; margin: 10px 0;'>
        <h4>📋 Report Interpretation</h4>
        <p>Help understand medical reports and test results in simple terms.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='padding: 15px; background-color: #e1f5fe; border-radius: 10px; margin: 10px 0;'>
        <h4>💡 Health Tips</h4>
        <p>Get personalized wellness advice and preventive care recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Health tips section
    st.subheader("💡 Daily Health Tips")
    
    if st.button("🎲 Get Random Health Tips"):
        with st.spinner("Generating health tips..."):
            try:
                tips = healthcare_ai.generate_health_tips("general")
                
                st.success("Today's Health Tips:")
                for i, tip in enumerate(tips[:3], 1):
                    st.write(f"{i}. {tip}")
                    
            except Exception as e:
                st.error(f"Unable to generate tips: {str(e)}")
    
    # Chat statistics
    if st.session_state.chat_history:
        st.subheader("📊 Chat Statistics")
        
        user_messages = len([m for m in st.session_state.chat_history if m['role'] == 'user'])
        ai_messages = len([m for m in st.session_state.chat_history if m['role'] == 'assistant'])
        
        st.metric("Your Messages", user_messages)
        st.metric("AI Responses", ai_messages)
        
        if st.session_state.chat_history:
            first_message = datetime.fromisoformat(st.session_state.chat_history[0]['timestamp'])
            duration = datetime.now() - first_message
            st.metric("Chat Duration", f"{duration.seconds // 60} minutes")

# Specialized AI functions section
st.markdown("---")
st.subheader("🔧 Specialized AI Functions")

# Create tabs for different AI functions
tab1, tab2, tab3 = st.tabs(["💊 Medication Check", "📋 Report Interpreter", "🏥 Health Assessment"])

with tab1:
    st.write("**Check medication interactions and get drug information**")
    
    medications_input = st.text_input(
        "Enter medications (separated by commas):",
        placeholder="e.g., Aspirin, Lisinopril, Metformin"
    )
    
    if st.button("Check Interactions", type="secondary") and medications_input:
        medications_list = [med.strip() for med in medications_input.split(',')]
        
        with st.spinner("Checking medication interactions..."):
            try:
                interaction_result = healthcare_ai.medication_interaction_check(medications_list)
                
                if 'error' not in interaction_result:
                    # Display results
                    severity = interaction_result.get('severity', 'Medium')
                    
                    if severity == 'High':
                        st.error(f"⚠️ **{severity} Risk Interactions Found**")
                    elif severity == 'Medium':
                        st.warning(f"🟡 **{severity} Risk Interactions**")
                    else:
                        st.success(f"✅ **{severity} Risk**")
                    
                    interactions = interaction_result.get('interactions', [])
                    if interactions:
                        st.write("**Potential Interactions:**")
                        for interaction in interactions:
                            st.write(f"• {interaction}")
                    
                    recommendations = interaction_result.get('recommendations', [])
                    if recommendations:
                        st.write("**Recommendations:**")
                        for rec in recommendations:
                            st.write(f"• {rec}")
                    
                    if interaction_result.get('consult_doctor', False):
                        st.warning("🩺 **Doctor consultation recommended**")
                
                else:
                    st.error(interaction_result.get('error', 'Unable to check interactions'))
                    
            except Exception as e:
                st.error(f"Error checking interactions: {str(e)}")

with tab2:
    st.write("**Get help understanding medical reports and test results**")
    
    report_text = st.text_area(
        "Paste your medical report or test results here:",
        placeholder="Copy and paste lab results, imaging reports, or other medical documents...",
        height=150
    )
    
    if st.button("Interpret Report", type="secondary") and report_text:
        with st.spinner("Interpreting medical report..."):
            try:
                interpretation = healthcare_ai.interpret_medical_report(report_text)
                
                st.success("📋 **Report Interpretation:**")
                st.write(interpretation)
                
                # Add to chat history
                st.session_state.chat_history.extend([
                    {
                        "role": "user",
                        "content": f"Please interpret this medical report: {report_text[:200]}...",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "role": "assistant",
                        "content": interpretation,
                        "timestamp": datetime.now().isoformat()
                    }
                ])
                
            except Exception as e:
                st.error(f"Error interpreting report: {str(e)}")

with tab3:
    st.write("**Get a comprehensive health assessment based on your information**")
    
    with st.form("health_assessment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age_input = st.number_input("Age", min_value=0, max_value=120, value=30)
            gender_input = st.selectbox("Gender", ["Male", "Female", "Other"])
            activity_level = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
        
        with col2:
            health_concerns = st.text_area("Current Health Concerns", placeholder="Any specific health issues or symptoms...")
            lifestyle_factors = st.text_area("Lifestyle Factors", placeholder="Diet, exercise, sleep, stress levels...")
        
        if st.form_submit_button("Get Health Assessment", type="primary"):
            assessment_prompt = f"""
            Please provide a comprehensive health assessment for:
            - Age: {age_input}
            - Gender: {gender_input}
            - Activity Level: {activity_level}
            - Health Concerns: {health_concerns or 'None specified'}
            - Lifestyle Factors: {lifestyle_factors or 'Not specified'}
            
            Include personalized recommendations for wellness, preventive care, and any areas of concern.
            """
            
            with st.spinner("Generating health assessment..."):
                try:
                    assessment = healthcare_ai.get_medical_advice(assessment_prompt)
                    
                    st.success("🏥 **Your Health Assessment:**")
                    st.write(assessment)
                    
                    # Add to chat history
                    st.session_state.chat_history.extend([
                        {
                            "role": "user",
                            "content": "I'd like a comprehensive health assessment based on my information.",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "role": "assistant",
                            "content": assessment,
                            "timestamp": datetime.now().isoformat()
                        }
                    ])
                    
                except Exception as e:
                    st.error(f"Error generating assessment: {str(e)}")

# Footer with important disclaimers
st.markdown("---")
st.markdown("""
<div style='padding: 20px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; margin: 20px 0;'>
    <h4>⚠️ Important Medical Disclaimer</h4>
    <p><strong>This AI assistant is for informational and educational purposes only.</strong></p>
    <ul>
        <li>🚫 Not a substitute for professional medical advice, diagnosis, or treatment</li>
        <li>🩺 Always seek the advice of qualified healthcare providers</li>
        <li>🚨 In case of medical emergency, call emergency services immediately</li>
        <li>💊 Never stop or change medications without consulting your doctor</li>
        <li>🔬 AI predictions and interpretations may not be 100% accurate</li>
    </ul>
    <p><em>By using this AI assistant, you acknowledge that you understand these limitations.</em></p>
</div>
""", unsafe_allow_html=True)

