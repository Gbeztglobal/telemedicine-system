from django.db import models
from accounts.models import User

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
