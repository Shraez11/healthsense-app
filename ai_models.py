import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import streamlit as st

class DiseasePredictor:
    """AI model for disease prediction based on symptoms."""
    
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.symptom_columns = []
        self.diseases = []
        self.init_model()
    
    def init_model(self):
        """Initialize and train the disease prediction model."""
        # Create synthetic training data for demonstration
        # In a real application, this would be loaded from a medical database
        symptoms_data = self._create_training_data()
        
        # Prepare features and target
        X = symptoms_data.drop(['disease', 'patient_id'], axis=1, errors='ignore')
        y = symptoms_data['disease']
        
        self.symptom_columns = X.columns.tolist()
        self.diseases = y.unique().tolist()
        
        # Encode target labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Train the model with enhanced parameters
        self.model = RandomForestClassifier(
            n_estimators=200,  # Increased from 100 for better accuracy
            max_depth=15,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42
        )
        self.model.fit(X, y_encoded)
    
    def _create_training_data(self):
        """Create synthetic training data for disease prediction."""
        np.random.seed(42)
        
        # Expanded symptoms list
        symptoms = [
            'fever', 'cough', 'fatigue', 'body_ache', 'headache', 'sore_throat',
            'runny_nose', 'shortness_of_breath', 'chest_pain', 'nausea',
            'vomiting', 'diarrhea', 'abdominal_pain', 'loss_of_appetite',
            'weight_loss', 'night_sweats', 'joint_pain', 'muscle_weakness',
            'dizziness', 'confusion', 'rash', 'itching', 'swelling',
            'back_pain', 'neck_pain', 'vision_problems', 'hearing_loss',
            'difficulty_swallowing', 'seizures', 'numbness', 'tingling',
            'frequent_urination', 'blood_in_urine', 'constipation', 'bloating'
        ]
        
        # Expanded disease patterns with more conditions
        disease_patterns = {
            'Common Cold': {
                'high_symptoms': ['runny_nose', 'sore_throat', 'cough'],
                'medium_symptoms': ['headache', 'fatigue'],
                'low_symptoms': ['fever']
            },
            'Influenza': {
                'high_symptoms': ['fever', 'body_ache', 'fatigue', 'headache'],
                'medium_symptoms': ['cough', 'sore_throat'],
                'low_symptoms': ['runny_nose']
            },
            'COVID-19': {
                'high_symptoms': ['fever', 'cough', 'fatigue', 'shortness_of_breath'],
                'medium_symptoms': ['headache', 'body_ache', 'sore_throat'],
                'low_symptoms': ['runny_nose', 'nausea', 'loss_of_appetite']
            },
            'Pneumonia': {
                'high_symptoms': ['fever', 'cough', 'shortness_of_breath', 'chest_pain'],
                'medium_symptoms': ['fatigue', 'body_ache'],
                'low_symptoms': ['headache']
            },
            'Gastroenteritis': {
                'high_symptoms': ['nausea', 'vomiting', 'diarrhea', 'abdominal_pain'],
                'medium_symptoms': ['fever', 'fatigue'],
                'low_symptoms': ['headache', 'loss_of_appetite']
            },
            'Migraine': {
                'high_symptoms': ['headache', 'nausea'],
                'medium_symptoms': ['fatigue', 'dizziness', 'vision_problems'],
                'low_symptoms': ['vomiting']
            },
            'Diabetes Type 2': {
                'high_symptoms': ['frequent_urination', 'fatigue', 'weight_loss'],
                'medium_symptoms': ['dizziness', 'vision_problems'],
                'low_symptoms': ['numbness', 'tingling']
            },
            'Hypertension': {
                'high_symptoms': ['headache', 'dizziness', 'vision_problems'],
                'medium_symptoms': ['chest_pain', 'fatigue'],
                'low_symptoms': ['nausea']
            },
            'Asthma': {
                'high_symptoms': ['shortness_of_breath', 'cough', 'chest_pain'],
                'medium_symptoms': ['fatigue'],
                'low_symptoms': ['dizziness']
            },
            'Urinary Tract Infection': {
                'high_symptoms': ['frequent_urination', 'blood_in_urine', 'abdominal_pain'],
                'medium_symptoms': ['fever', 'back_pain'],
                'low_symptoms': ['fatigue']
            },
            'Arthritis': {
                'high_symptoms': ['joint_pain', 'swelling', 'muscle_weakness'],
                'medium_symptoms': ['fatigue', 'body_ache'],
                'low_symptoms': ['fever']
            },
            'Allergic Reaction': {
                'high_symptoms': ['rash', 'itching', 'swelling'],
                'medium_symptoms': ['shortness_of_breath', 'nausea'],
                'low_symptoms': ['dizziness']
            },
            'Bronchitis': {
                'high_symptoms': ['cough', 'chest_pain', 'fatigue'],
                'medium_symptoms': ['sore_throat', 'fever'],
                'low_symptoms': ['headache', 'body_ache']
            },
            'Strep Throat': {
                'high_symptoms': ['sore_throat', 'fever', 'difficulty_swallowing'],
                'medium_symptoms': ['headache', 'body_ache'],
                'low_symptoms': ['nausea']
            },
            'Sinusitis': {
                'high_symptoms': ['headache', 'runny_nose', 'facial_pain'],
                'medium_symptoms': ['cough', 'fever'],
                'low_symptoms': ['fatigue']
            }
        }
        
        # Add facial_pain to symptoms if referenced
        if 'facial_pain' not in symptoms:
            symptoms.append('facial_pain')
        
        # Generate training data with larger dataset for better model performance
        data = []
        for _ in range(2500):  # Increased from 1000 to 2500 samples
            disease = np.random.choice(list(disease_patterns.keys()))
            pattern = disease_patterns[disease]
            
            # Create symptom vector
            symptom_vector = {symptom: 0 for symptom in symptoms}
            
            # Set high probability symptoms
            for symptom in pattern['high_symptoms']:
                if symptom in symptom_vector:
                    symptom_vector[symptom] = np.random.choice([0, 1], p=[0.2, 0.8])
            
            # Set medium probability symptoms
            for symptom in pattern['medium_symptoms']:
                if symptom in symptom_vector:
                    symptom_vector[symptom] = np.random.choice([0, 1], p=[0.5, 0.5])
            
            # Set low probability symptoms
            for symptom in pattern['low_symptoms']:
                if symptom in symptom_vector:
                    symptom_vector[symptom] = np.random.choice([0, 1], p=[0.8, 0.2])
            
            # Add some noise
            for symptom in symptoms:
                if symptom not in pattern['high_symptoms'] + pattern['medium_symptoms'] + pattern['low_symptoms']:
                    symptom_vector[symptom] = np.random.choice([0, 1], p=[0.95, 0.05])
            
            symptom_vector['disease'] = disease
            data.append(symptom_vector)
        
        return pd.DataFrame(data)
    
    def predict_disease(self, symptoms):
        """
        Predict disease based on symptoms.
        
        Args:
            symptoms (dict): Dictionary of symptoms with boolean values
        
        Returns:
            dict: Prediction results with disease, probability, and confidence
        """
        if self.model is None:
            return {"error": "Model not initialized"}
        
        # Create feature vector
        feature_vector = []
        for symptom in self.symptom_columns:
            feature_vector.append(1 if symptoms.get(symptom, False) else 0)
        
        # Make prediction
        prediction = self.model.predict([feature_vector])[0]
        probabilities = self.model.predict_proba([feature_vector])[0]
        
        # Get disease name
        disease = self.label_encoder.inverse_transform([prediction])[0]
        confidence = max(probabilities)
        
        # Get top 3 predictions
        top_indices = np.argsort(probabilities)[-3:][::-1]
        top_predictions = []
        
        for idx in top_indices:
            disease_name = self.label_encoder.inverse_transform([idx])[0]
            probability = probabilities[idx]
            top_predictions.append({
                'disease': disease_name,
                'probability': float(probability)
            })
        
        return {
            'primary_prediction': disease,
            'confidence': float(confidence),
            'top_predictions': top_predictions,
            'total_symptoms': sum(feature_vector)
        }
    
    def get_available_symptoms(self):
        """Get list of available symptoms for input."""
        return self.symptom_columns
    
    def get_symptom_importance(self, symptoms):
        """Get feature importance for the given symptoms."""
        if self.model is None:
            return {}
        
        feature_importance = self.model.feature_importances_
        importance_dict = {}
        
        for i, symptom in enumerate(self.symptom_columns):
            if symptoms.get(symptom, False):
                importance_dict[symptom] = float(feature_importance[i])
        
        return importance_dict

@st.cache_resource
def get_disease_predictor():
    """Get cached instance of disease predictor."""
    return DiseasePredictor()
