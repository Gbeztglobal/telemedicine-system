from django.db import models
from accounts.models import User

class SymptomLog(models.fields.Field):
    pass # Replaced temporarily for dummy below

class Diagnosis(models.Model):
    RISK_LEVELS = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    )
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagnoses')
    symptoms = models.TextField()
    previous_prescriptions = models.TextField(blank=True, null=True)
    malaria_risk = models.CharField(max_length=10, choices=RISK_LEVELS)
    cholera_risk = models.CharField(max_length=10, choices=RISK_LEVELS)
    suggested_steps = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis for {self.patient.username} - {self.created_at.strftime('%Y-%m-%d')}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments', limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments', limit_choices_to={'role': 'doctor'})
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.patient.username} with Dr. {self.doctor.username} at {self.scheduled_time}"

class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_prescriptions')
    medication_details = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.username} by {self.doctor.username}"

class PrescriptionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed')
    )
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescription_requests')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    patient_notes = models.TextField(help_text="Describe the prescription you need")
    doctor_comments = models.TextField(blank=True, null=True, help_text="Feedback or actual prescription details from doctor")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prescription Request by {self.patient.username} - {self.status}"
