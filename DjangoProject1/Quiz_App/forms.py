from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Classroom, Question
from .models import Quiz
from django.utils.timezone import now

class SignupForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'})
    )
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    role = forms.ChoiceField(
        choices=[('', 'Select your role'), ('student', 'Student'), ('teacher', 'Teacher')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        required=True
    )
    reenter_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter your password'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        reenter_password = cleaned_data.get('reenter_password')

        if password and reenter_password and password != reenter_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash password
        if commit:
            user.save()
            # Create a Profile with role selection
            role = self.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
        return user

class JoinClassForm(forms.Form):
    class_code = forms.CharField(
        max_length=7,
        min_length=5,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'classCode',
                'placeholder': 'Class code',
                'required': 'required',
            }
        ),
    )


class AddStudentForm(forms.Form):
    email_or_username = forms.CharField(
        max_length=254,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email or username',
            'aria-label': 'Email or Username'
        })
    )

# Fetch Data from User in Profile Management
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'firstName'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'lastName'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'}),
        }

class CustomSignupForm(SignupForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label="Role")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")

    def save(self, request):
        user = super().save(request)
        user.profile.role = self.cleaned_data['role']
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

# Django Form for Creating Class
class CreateClassForm(forms.Form):
    class_name = forms.CharField(label='Class Name', max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter class name'
    }))
    section = forms.CharField(label='Section', max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter section'
    }))
    subject = forms.CharField(label='Subject', max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter subject'
    }))
    room = forms.CharField(label='Room', max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter room'
    }))


# Change Password Forms.
class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'currentPassword'}),
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'newPassword'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'confirmPassword'}),
        label="Confirm New Password"
    )


class EditClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['class_name', 'room', 'section', 'subject']
        # Define widgets to style and customize form fields
        widgets = {
            'class_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'className'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'id': 'room'}),
            'section': forms.TextInput(attrs={'class': 'form-control', 'id': 'section'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'id': 'subject'}),
        }

# Jdango Form for Login using the Authentication
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',  # Adjust placeholder
            'id': 'username_or_email'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'password'
        }),
    )

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'due_date', 'description', 'timer']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'title',
                'placeholder': 'Enter Quiz Title'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'id': 'due_date',
                'placeholder': 'dd/mm/yyyy --:--',
                'type': 'datetime-local',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'description',
                'rows': 4,
                'placeholder': 'Enter Quiz Description (optional)',
            }),
            'timer': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'timer',
                'placeholder': 'Enter timer in minutes',
                'min': 1,
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timer'].required = True
        self.fields['due_date'].required = True

    def clean_timer(self):
        """Ensure the timer is a positive integer."""
        timer = self.cleaned_data.get('timer')
        if timer is None or timer < 1:
            raise forms.ValidationError("The timer must be a positive integer (minimum 1 minute).")
        return timer

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date < now():
            raise forms.ValidationError("The due date cannot be in the past.")
        return due_date



class QuestionForm(forms.Form):
    question_text = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter question text'
        }),
        required=True
    )
    multiple_choice_options = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Option 1\nOption 2\nOption 3',
            'rows': 3
        }),
        required=False
    )
    answer = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter correct answer'
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        quiz_type = kwargs.pop('quiz_type', None)
        super().__init__(*args, **kwargs)

        if quiz_type == 'multiple_choice':
            self.fields['multiple_choice_options'].required = True
            self.fields['answer'].widget.attrs['placeholder'] = 'Enter correct option number (e.g., 1)'
        elif quiz_type == 'true_false':
            self.fields['multiple_choice_options'].widget = forms.HiddenInput()
            self.fields['answer'] = forms.ChoiceField(
                choices=[('True', 'True'), ('False', 'False')],
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        elif quiz_type == 'identification':
            self.fields['multiple_choice_options'].widget = forms.HiddenInput()
            self.fields['answer'].widget.attrs['placeholder'] = 'Enter correct answer'

    def clean(self):
        cleaned_data = super().clean()
        quiz_type = self.initial.get('quiz_type')
        answer = cleaned_data.get('answer')
        options = cleaned_data.get('multiple_choice_options')

        if quiz_type == 'multiple_choice':
            if not options:
                raise forms.ValidationError("You must provide options for a multiple-choice question.")
            options_list = options.split("\n")
            if not answer.isdigit() or int(answer) < 1 or int(answer) > len(options_list):
                raise forms.ValidationError("The correct answer must be a valid option number.")
        elif quiz_type == 'true_false':
            if answer not in ['True', 'False']:
                raise forms.ValidationError("The correct answer for True/False must be 'True' or 'False'.")
        elif quiz_type == 'identification':
            if not answer:
                raise forms.ValidationError("You must provide the correct answer for an identification question.")

        return cleaned_data

class BaseQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'multiple_choice_options', 'correct_answers']
        widgets = {
            'question_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the question text'
            }),
            'question_type': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'toggleOptions(this)'  # Custom JS to toggle options
            }),
            'multiple_choice_options': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter each option on a new line',
                'rows': 4
            }),
            'correct_answers': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter correct answers (comma-separated for multiple)',
                'rows': 2
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        multiple_choice_options = cleaned_data.get('multiple_choice_options')
        correct_answers = cleaned_data.get('correct_answers')

        if question_type == 'multiple_choice' and not multiple_choice_options:
            raise ValidationError("Multiple choice questions must have options.")
        if not correct_answers:
            raise ValidationError("Please provide correct answer(s).")
        return cleaned_data

class AddQuestionForm(BaseQuestionForm):
    pass  # No additional logic required for adding

class EditQuestionForm(BaseQuestionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.question_type == 'true_false':
            self.fields['multiple_choice_options'].widget = forms.HiddenInput()
