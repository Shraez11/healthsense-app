from datetime import datetime, timedelta
import streamlit as st

class NotificationService:
    """Service for sending email and SMS notifications"""
    
    def __init__(self):
        self.email_enabled = False  # Will be True when SendGrid/Resend is integrated
        self.sms_enabled = False    # Will be True when Twilio is integrated
    
    def send_email(self, to_email, subject, body):
        """Send email notification"""
        # Placeholder - will be implemented with SendGrid/Resend integration
        print(f"[EMAIL] To: {to_email}, Subject: {subject}")
        print(f"[EMAIL] Body: {body}")
        return True
    
    def send_sms(self, to_phone, message):
        """Send SMS notification"""
        # Placeholder - will be implemented with Twilio integration
        print(f"[SMS] To: {to_phone}")
        print(f"[SMS] Message: {message}")
        return True
    
    def send_appointment_reminder(self, appointment, patient):
        """Send appointment reminder to patient"""
        # Format appointment details
        appointment_date = appointment['date']
        appointment_time = appointment['time']
        doctor = appointment['doctor']
        
        # Email notification
        email_subject = "🏥 Appointment Reminder - HealthSense"
        email_body = f"""
Dear {patient['name']},

This is a reminder for your upcoming appointment:

📅 Date: {appointment_date}
🕐 Time: {appointment_time}
👨‍⚕️ Doctor: Dr. {doctor}
🏥 Department: {appointment.get('department', 'General')}

Please arrive 10 minutes early for check-in.

If you need to reschedule, please contact us at least 24 hours in advance.

Best regards,
HealthSense Team
        """
        
        # SMS notification
        sms_message = f"HealthSense Reminder: Appointment with Dr. {doctor} on {appointment_date} at {appointment_time}. Reply CONFIRM to confirm."
        
        # Send notifications
        if patient.get('email'):
            self.send_email(patient['email'], email_subject, email_body)
        
        if patient.get('phone'):
            self.send_sms(patient['phone'], sms_message)
        
        return True
    
    def send_prescription_notification(self, prescription, patient):
        """Send prescription notification to patient"""
        medication = prescription['medication_name']
        
        email_subject = "💊 New Prescription - HealthSense"
        email_body = f"""
Dear {patient['name']},

A new prescription has been issued for you:

💊 Medication: {medication}
📏 Dosage: {prescription['dosage']}
⏰ Frequency: {prescription['frequency']}
📝 Instructions: {prescription.get('instructions', 'As directed by physician')}

Please collect your medication from the pharmacy.

Best regards,
HealthSense Team
        """
        
        sms_message = f"New prescription: {medication} {prescription['dosage']}. Collect from pharmacy. -HealthSense"
        
        if patient.get('email'):
            self.send_email(patient['email'], email_subject, email_body)
        
        if patient.get('phone'):
            self.send_sms(patient['phone'], sms_message)
        
        return True
    
    def send_test_results_notification(self, record, patient):
        """Send medical test results notification"""
        email_subject = "🔬 Test Results Available - HealthSense"
        email_body = f"""
Dear {patient['name']},

Your test results are now available:

📋 Test: {record['title']}
📅 Date: {record['date']}
👨‍⚕️ Doctor: Dr. {record['doctor']}

Please log in to your HealthSense account to view your results, or contact your physician for details.

Best regards,
HealthSense Team
        """
        
        if patient.get('email'):
            self.send_email(patient['email'], email_subject, email_body)
        
        return True

def schedule_appointment_reminders(data_manager):
    """Schedule reminders for upcoming appointments"""
    notification_service = NotificationService()
    
    # Get appointments for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    appointments = data_manager.get_appointments_by_date(tomorrow)
    
    reminders_sent = 0
    for appointment in appointments:
        if appointment['status'] == 'Scheduled':
            patient = data_manager.get_patient_by_id(appointment['patient_id'])
            if patient:
                notification_service.send_appointment_reminder(appointment, patient)
                reminders_sent += 1
    
    return reminders_sent
