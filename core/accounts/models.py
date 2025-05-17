# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Area(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=1, unique=True)
    
    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='regions')
    
    def __str__(self):
        return f"{self.name} ({self.area.name})"

class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('pacient', 'Pacient'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES, default='pacient')
    phone = models.CharField(max_length=20, blank=True)
    iin = models.CharField(max_length=12, unique=True, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    ticket = models.CharField(max_length=8, unique=True, blank=True)
    link = models.URLField(max_length=200, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.ticket and self.area:
            last_user = CustomUser.objects.filter(area=self.area).order_by('ticket').last()
            if last_user and last_user.ticket:
                number = int(last_user.ticket[1:]) + 1
            else:
                number = 1
            self.ticket = f"{self.area.code}{number:07d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.ticket})"
