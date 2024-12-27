from django.db import models
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def save(self, request):
        user = super().save(request)
        role = self.cleaned_data.get('role')
        Profile.objects.create(user=user, role=role)  # Assuming a Profile model for role
        return user

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

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='quizzes')
    due_date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    timer = models.PositiveIntegerField(help_text="Duration of the quiz in minutes", default=30)
    is_active = models.BooleanField(default=True)  # Add this field

    def __str__(self):
        return f"{self.title} ({self.classroom.class_name})"


class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('identification', 'Identification'),
    ]

    quizzes = models.ManyToManyField(Quiz, related_name='questions', blank=True)
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)

    # Fields for specific question types
    multiple_choice_options = models.TextField(
        blank=True,
        null=True,
        help_text="Provide options separated by newlines. Only for Multiple Choice."
    )
    correct_answers = models.TextField(
        blank=True,
        default='',
        help_text=(
            "Correct answer(s): "
            "For Multiple Choice, provide options separated by newlines. "
            "For True/False, use 'True' or 'False'. "
            "For Identification, provide the exact text of the correct answer(s)."
        )
    )

    def options_as_list(self):
        """
        Return multiple choice options as a list.
        """
        return self.multiple_choice_options.split("\n") if self.multiple_choice_options else []

    def correct_answers_as_list(self):
        """
        Return correct answers as a list.
        """
        return self.correct_answers.split("\n") if self.correct_answers else []

    def is_answer_correct(self, user_answer):
        """
        Check if a provided answer is correct with exact case-sensitive matching.
        """
        print(f"Question: {self.question_text}")
        print(f"User Answer: {user_answer}")
        print(f"Correct Answers: {self.correct_answers_as_list()}")

        if self.question_type == 'true_false':
            # Direct case-sensitive match for True/False
            return user_answer.strip() == self.correct_answers.strip()
        elif self.question_type in ['multiple_choice', 'identification']:
            # Exact case-sensitive match for multiple choice or identification
            correct = [answer.strip() for answer in self.correct_answers_as_list()]
            return user_answer.strip() in correct
        return False

    def clean(self):
        """
        Custom validation for question fields based on `question_type`.
        """
        from django.core.exceptions import ValidationError

        if self.question_type == 'multiple_choice':
            if not self.multiple_choice_options:
                raise ValidationError("Multiple choice questions must have options.")
        elif self.question_type == 'true_false':
            if self.correct_answers.strip().lower() not in ['true', 'false']:
                raise ValidationError("True/False questions must have 'True' or 'False' as the correct answer.")
        elif self.question_type == 'identification':
            if not self.correct_answers:
                raise ValidationError("Identification questions must have at least one correct answer.")

    def save(self, *args, **kwargs):
        """
        Override save to include custom validation.
        """
        self.full_clean()  # Call clean method before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Question: {self.question_text} (Type: {self.question_type})"

class StudentQuizScore(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}/{self.total_questions}"

class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="responses")
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.TextField()
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Response to '{self.question}' by {self.student.username}"
