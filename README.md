# HealthSense - AI-Powered Healthcare Management System

## Overview

HealthSense is a comprehensive healthcare management platform built with Streamlit that combines patient management, appointment scheduling, medical records, prescriptions, and AI-powered disease prediction capabilities. The system provides a complete digital healthcare solution with role-based authentication, real-time analytics, and an AI chatbot assistant.

The application serves healthcare providers with tools to manage patients, track medical histories, schedule appointments, generate prescriptions, predict diseases based on symptoms, and analyze health trends - all through an intuitive web interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based multi-page application
- **UI Pattern**: Page-based navigation with sidebar controls
- **Styling**: Custom CSS with healthcare-themed gradients and color schemes (primary colors: #2E86AB, #A23B72)
- **State Management**: Streamlit session state for client-side data persistence and caching
- **Visualization**: Plotly for interactive charts and graphs (Express and Graph Objects)

### Backend Architecture
- **Application Structure**: Multi-page Streamlit app with modular page organization
  - Main app dashboard (`app.py`)
  - Login/authentication page (`Login.py`)
  - Feature pages under `/pages` directory (Patient Management, Appointments, Medical Records, Prescriptions, Disease Prediction, AI Chatbot, Analytics)
- **Data Layer**: Dual persistence strategy
  - Session-based storage via `DataManager` (Streamlit session state)
  - Database persistence via `DatabaseManager` (SQLAlchemy ORM)
- **Business Logic**: Utility modules for specialized functionality
  - Authentication and authorization (`utils/auth.py`)
  - AI/ML models (`utils/ai_models.py`)
  - PDF generation (`utils/pdf_generator.py`)
  - Notifications (`utils/notifications.py`)
  - OpenAI integration (`utils/openai_client.py`)

### Authentication & Authorization
- **Authentication System**: Custom-built using SQLAlchemy and bcrypt
- **Password Security**: Bcrypt hashing with salt (upgraded from legacy SHA-256)
- **Session Management**: Streamlit session state with user context
- **Role-Based Access**: Three roles supported - admin, doctor, patient
- **User Model**: Includes username, email, password hash, full name, role, active status

### AI/ML Components
- **Disease Prediction**: Random Forest Classifier with synthetic training data
  - 200 estimators, max depth 15
  - Symptom-based prediction across multiple disease categories
  - Confidence scoring and feature importance analysis
- **AI Chatbot**: OpenAI GPT-5 integration
  - Context-aware medical advice with patient information
  - Healthcare-specific system prompts
  - Disclaimer about professional medical consultation
- **Model Architecture**: Scikit-learn based with label encoding for disease classification

### Data Models
- **Patient**: Comprehensive demographics, medical history, insurance, emergency contacts
- **Appointment**: Scheduling with patient linking, doctor assignment, status tracking
- **MedicalRecord**: Diagnosis, symptoms, lab results, treatment plans
- **Prescription**: Medication details, dosage, duration, refill tracking
- **DiseasePrediction**: AI prediction results with symptoms, confidence scores
- **User**: Authentication and role management

### Document Generation
- **PDF Reports**: ReportLab-based generation
  - Prescriptions with patient and doctor information
  - Medical records with formatted styling
  - Custom healthcare-themed templates with color coding

## External Dependencies

### Core Framework
- **Streamlit**: Web application framework and UI
- **Python 3.x**: Runtime environment

### Database & ORM
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database (via DATABASE_URL environment variable)
- **Database Tables**: patients, appointments, medical_records, prescriptions, disease_predictions, users

### AI & Machine Learning
- **OpenAI API**: GPT-5 model for AI chatbot functionality
  - Requires OPENAI_API_KEY environment variable
  - Healthcare-specific prompt engineering
- **Scikit-learn**: Machine learning models (RandomForestClassifier, LabelEncoder)
- **NumPy**: Numerical computations for ML
- **Pandas**: Data manipulation and analysis

### Visualization & Reporting
- **Plotly**: Interactive charts (plotly.express and plotly.graph_objects)
- **ReportLab**: PDF document generation

### Security
- **bcrypt**: Password hashing and verification
- **UUID**: Unique identifier generation

### Notification Services
- **Email**: Resend/SendGrid integration available via Replit connectors (user dismissed integration setup)
  - To enable email notifications: Set up Resend connector and update `utils/notifications.py` to use Resend API
- **SMS**: Twilio integration available via Replit connectors (not configured)
  - To enable SMS notifications: Set up Twilio connector and update `utils/notifications.py` to use Twilio API
- Current implementation uses console logging as placeholder
- Note: Notification framework is fully implemented with appointment reminders, prescription alerts, and test result notifications ready to activate once credentials are provided

### Environment Configuration
Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API authentication

### Data Persistence Strategy
The application uses a hybrid approach:
1. **Session State**: Temporary data via `DataManager` for quick operations
2. **Database**: Persistent storage via `DatabaseManager` with SQLAlchemy
3. **Caching**: Streamlit `@st.cache_resource` for database manager and AI client instances
