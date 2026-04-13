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
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    @property
    def profile_picture(self):
        # Compatibility property to prevent crashes if old cached logic looks for this
        return type('obj', (object,), {'url': self.avatar_url})

    @property
    def avatar_url(self):
        # Prefer uploaded avatar if it exists
        if self.avatar:
            return self.avatar.url
            
        # Fallback to DiceBear Avataaars style
        gender_seed = getattr(self, 'gender', 'male') or 'male'
        username_seed = getattr(self, 'username', 'guest')
        style = "avataaars"
        seed = f"{gender_seed}_{username_seed}"
        return f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
