from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Classroom(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)  # Teacher who created the class
    class_name = models.CharField(max_length=100)
    section = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    room = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class_code = models.CharField(max_length=7, null=False, blank=True)  # Class code for joining
    students = models.ManyToManyField(User, related_name='classrooms', blank=True)  # Add this line

    def __str__(self):
        return f"{self.class_name} - {self.section}"