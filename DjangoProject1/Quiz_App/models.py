from django.db import models
from django.contrib.auth.models import User
import uuid


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
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'teacher'})
    class_name = models.CharField(max_length=100)
    section = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    room = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class_code = models.CharField(max_length=7, unique=True, default=uuid.uuid4().hex[:7].upper())
    students = models.ManyToManyField(User, related_name='classrooms', blank=True, limit_choices_to={'profile__role': 'student'})

    def __str__(self):
        return f"{self.class_name} - {self.section}"


class Quiz(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    reused_questions = models.ManyToManyField('Question', blank=True, related_name='reused_in_quizzes')

    def __str__(self):
        return f"{self.title} - {self.classroom.class_name}"


class Question(models.Model):
    QUIZ_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('tf', 'True/False'),
        ('identification', 'Identification'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUIZ_CHOICES)
    points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quiz.title} - {self.question_text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.question_text[:50]} - {self.choice_text}"


class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'})
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


class Answer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.submission.student.username} - {self.question.question_text[:50]}"
