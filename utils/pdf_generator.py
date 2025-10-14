from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import io

class PDFGenerator:
    """Generate PDF reports for medical documents"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=12
        )
    
    def generate_prescription_pdf(self, prescription, patient, doctor_name):
        """Generate prescription PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("🏥 HealthSense - Medical Prescription", self.title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", self.heading_style))
        patient_data = [
            ['Name:', patient['name']],
            ['Age:', str(patient.get('age', 'N/A'))],
            ['Gender:', patient.get('gender', 'N/A')],
            ['Blood Group:', patient.get('blood_group', 'N/A')],
            ['Date:', prescription['date_prescribed']]
        ]
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Prescription Details
        story.append(Paragraph("Prescription Details", self.heading_style))
        rx_data = [
            ['Medication:', prescription['medication_name']],
            ['Dosage:', prescription['dosage']],
            ['Frequency:', prescription['frequency']],
            ['Duration:', prescription.get('duration', 'As directed')],
            ['Quantity:', str(prescription['quantity'])],
            ['Refills:', str(prescription.get('refills_remaining', 0))]
        ]
        rx_table = Table(rx_data, colWidths=[2*inch, 4*inch])
        rx_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(rx_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Instructions
        if prescription.get('instructions'):
            story.append(Paragraph("Instructions", self.heading_style))
            story.append(Paragraph(prescription['instructions'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Warnings
        if prescription.get('warnings'):
            story.append(Paragraph("Warnings", self.heading_style))
            story.append(Paragraph(prescription['warnings'], self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Doctor signature
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Dr. {doctor_name}", self.styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_medical_report_pdf(self, record, patient):
        """Generate medical report PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("🏥 HealthSense - Medical Report", self.title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", self.heading_style))
        patient_data = [
            ['Name:', patient['name']],
            ['Age:', str(patient.get('age', 'N/A'))],
            ['Gender:', patient.get('gender', 'N/A')],
            ['Patient ID:', patient['id'][:8]]
        ]
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Report Details
        story.append(Paragraph("Report Details", self.heading_style))
        report_data = [
            ['Type:', record['record_type']],
            ['Title:', record['title']],
            ['Date:', record['date']],
            ['Doctor:', f"Dr. {record['doctor']}"],
            ['Department:', record.get('department', 'N/A')]
        ]
        report_table = Table(report_data, colWidths=[2*inch, 4*inch])
        report_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(report_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Description
        if record.get('description'):
            story.append(Paragraph("Description", self.heading_style))
            story.append(Paragraph(record['description'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Findings
        if record.get('findings'):
            story.append(Paragraph("Findings", self.heading_style))
            story.append(Paragraph(record['findings'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Lab Values
        if record.get('lab_values'):
            story.append(Paragraph("Laboratory Values", self.heading_style))
            lab_data = []
            for key, value in record['lab_values'].items():
                lab_data.append([key.replace('_', ' ').title(), str(value)])
            
            lab_table = Table(lab_data, colWidths=[2.5*inch, 2.5*inch])
            lab_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(lab_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        if record.get('recommendations'):
            story.append(Paragraph("Recommendations", self.heading_style))
            story.append(Paragraph(record['recommendations'], self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Paragraph("HealthSense - AI-Powered Healthcare Management", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_patient_summary_pdf(self, patient, appointments, prescriptions, records):
        """Generate comprehensive patient summary PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("🏥 HealthSense - Patient Summary Report", self.title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information
        story.append(Paragraph("Patient Information", self.heading_style))
        patient_data = [
            ['Name:', patient['name']],
            ['Age:', str(patient.get('age', 'N/A'))],
            ['Gender:', patient.get('gender', 'N/A')],
            ['Blood Group:', patient.get('blood_group', 'N/A')],
            ['Email:', patient.get('email', 'N/A')],
            ['Phone:', patient.get('phone', 'N/A')]
        ]
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Medical History
        if patient.get('medical_history'):
            story.append(Paragraph("Medical History", self.heading_style))
            story.append(Paragraph(patient['medical_history'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Active Prescriptions
        if prescriptions:
            story.append(Paragraph(f"Active Prescriptions ({len(prescriptions)})", self.heading_style))
            active_rx = [p for p in prescriptions if p['status'] == 'Active']
            if active_rx:
                rx_data = [['Medication', 'Dosage', 'Frequency']]
                for rx in active_rx[:10]:  # Limit to 10
                    rx_data.append([rx['medication_name'], rx['dosage'], rx['frequency']])
                
                rx_table = Table(rx_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
                rx_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
                ]))
                story.append(rx_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Recent Appointments
        if appointments:
            story.append(Paragraph(f"Recent Appointments ({len(appointments)})", self.heading_style))
            apt_data = [['Date', 'Doctor', 'Status']]
            for apt in appointments[:5]:  # Limit to 5
                apt_data.append([apt['date'], f"Dr. {apt['doctor']}", apt['status']])
            
            apt_table = Table(apt_data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
            apt_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
            ]))
            story.append(apt_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Paragraph("HealthSense - AI-Powered Healthcare Management", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
