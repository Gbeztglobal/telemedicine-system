from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor (Health Worker)'),
    )
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    phone_number = models.CharField(max_length=15, blank=False, null=False)

    @property
    def avatar_url(self):
        # Using DiceBear Avataaars style
        # Male/Female seeds to help with style, username for uniqueness
        style = "avataaars"
        seed = f"{self.gender}_{self.username}"
        return f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
