import os
import json
from openai import OpenAI

class HealthcareAI:
    """AI client for healthcare-related queries and chatbot functionality."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))
    
    def get_medical_advice(self, query, patient_context=None):
        """
        Get AI-powered medical advice and information.
        
        Args:
            query (str): User's medical question
            patient_context (dict): Optional patient context information
        
        Returns:
            str: AI response with medical advice
        """
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        system_prompt = """You are a knowledgeable healthcare AI assistant. Provide helpful, 
        accurate medical information while always emphasizing that your advice should not replace 
        professional medical consultation. Always recommend consulting with healthcare professionals 
        for serious concerns. Be empathetic, clear, and provide actionable guidance when appropriate."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if patient_context:
            context_info = f"""Patient Context:
            - Age: {patient_context.get('age', 'Not specified')}
            - Gender: {patient_context.get('gender', 'Not specified')}
            - Medical History: {patient_context.get('medical_history', 'Not available')}
            - Current Medications: {patient_context.get('medications', 'None listed')}
            
            Question: {query}"""
        else:
            context_info = query
        
        messages.append({"role": "user", "content": context_info})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                max_completion_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    def analyze_symptoms(self, symptoms, patient_info=None):
        """
        Analyze symptoms and provide preliminary assessment.
        
        Args:
            symptoms (list): List of symptoms
            patient_info (dict): Patient information for context
        
        Returns:
            dict: Analysis results with recommendations
        """
        symptoms_text = ", ".join(symptoms)
        
        prompt = f"""As a healthcare AI, analyze these symptoms: {symptoms_text}
        
        Please provide:
        1. Possible conditions to consider
        2. Urgency level (Low, Medium, High, Emergency)
        3. Recommended next steps
        4. When to seek immediate medical attention
        
        Respond in JSON format with keys: conditions, urgency, recommendations, warning_signs"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are a medical analysis AI. Provide structured analysis of symptoms."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=1024
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "error": f"Unable to analyze symptoms: {str(e)}",
                "urgency": "Medium",
                "recommendations": ["Please consult with a healthcare professional"],
                "warning_signs": ["Any worsening of symptoms"]
            }
    
    def generate_health_tips(self, category="general"):
        """
        Generate personalized health tips.
        
        Args:
            category (str): Category of health tips (general, diet, exercise, mental_health)
        
        Returns:
            list: List of health tips
        """
        prompt = f"""Generate 5 practical and actionable {category} health tips. 
        Make them specific, easy to implement, and evidence-based. 
        Format as a JSON list of tips."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are a health and wellness expert providing practical advice."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=1024
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("tips", ["Stay hydrated", "Get regular exercise", "Maintain good sleep hygiene"])
        except Exception as e:
            return [
                "Stay hydrated by drinking 8 glasses of water daily",
                "Get at least 30 minutes of moderate exercise most days",
                "Aim for 7-9 hours of quality sleep each night",
                "Eat a balanced diet rich in fruits and vegetables",
                "Practice stress management techniques regularly"
            ]
    
    def interpret_medical_report(self, report_text):
        """
        Help interpret medical reports in simple language.
        
        Args:
            report_text (str): Medical report content
        
        Returns:
            str: Simplified explanation
        """
        prompt = f"""Please explain this medical report in simple, understandable language:

        {report_text}

        Focus on:
        1. What the results mean
        2. Any values outside normal ranges
        3. What the patient should understand
        4. Follow-up recommendations

        Use non-medical terminology where possible."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are a medical interpreter helping patients understand their medical reports."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1024
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"I'm unable to interpret the report at this time. Please consult with your healthcare provider for clarification. Error: {str(e)}"
    
    def medication_interaction_check(self, medications):
        """
        Check for potential medication interactions.
        
        Args:
            medications (list): List of medications
        
        Returns:
            dict: Interaction analysis
        """
        meds_text = ", ".join(medications)
        
        prompt = f"""Analyze potential interactions between these medications: {meds_text}

        Provide analysis in JSON format with:
        - interactions: list of potential interactions
        - severity: overall severity level (Low, Medium, High)
        - recommendations: list of recommendations
        - consult_doctor: boolean indicating if doctor consultation is needed"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical AI analyzing medication interactions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=1024
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "error": f"Unable to check interactions: {str(e)}",
                "severity": "Medium",
                "recommendations": ["Consult with your pharmacist or doctor"],
                "consult_doctor": True
            }
