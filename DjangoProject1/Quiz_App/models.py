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

# Add the Quiz model
class Quiz(models.Model):
    QUIZ_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('identification', 'Identification'),
    ]

    title = models.CharField(max_length=255)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='quizzes')
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES)
    due_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.classroom.class_name}"

class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('identification', 'Identification'),
    ]

    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    multiple_choice_options = models.TextField(blank=True, null=True)  # Options for MCQ
    correct_answers = models.TextField(blank=True, null=True)  # New field for multiple correct answers

    def options_as_list(self):
        """Convert multiple_choice_options to a list."""
        return self.multiple_choice_options.split("\n") if self.multiple_choice_options else []

    def correct_answers_as_list(self):
        """Convert correct_answers to a list."""
        return self.correct_answers.split("\n") if self.correct_answers else []

    def __str__(self):
        return self.question_text


