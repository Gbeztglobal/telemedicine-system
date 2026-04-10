from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor (Health Worker)'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    profile_picture = models.ImageField(upload_to='profiles/', default='profiles/default.png', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
