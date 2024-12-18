from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Classroom
from .models import Quiz

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
        fields = ['title', 'quiz_type', 'due_date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'title',
                'placeholder': 'Enter Quiz Title'
            }),
            'quiz_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'quiz_type'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'id': 'due_date',
                'placeholder': 'dd/mm/yyyy --:--'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'description',
                'rows': 4,
                'placeholder': 'Enter Quiz Description'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)
        # Explicitly set choices without any placeholder option
        self.fields['quiz_type'].choices = [
            ('multiple_choice', 'Multiple Choice'),
            ('true_false', 'True/False'),
            ('identification', 'Identification'),
        ]
        self.fields['quiz_type'].required = True  # Ensure the field is required

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
        quiz_type = kwargs.pop('quiz_type', None)  # Dynamically pass 'quiz_type'
        super().__init__(*args, **kwargs)

        # Adjust form fields based on the quiz type
        if quiz_type == 'multiple_choice':
            self.fields['multiple_choice_options'].required = True
            self.fields['answer'].widget.attrs['placeholder'] = 'Enter correct option number'
        elif quiz_type == 'true_false':
            self.fields['multiple_choice_options'].widget = forms.HiddenInput()  # Hide options
            self.fields['answer'] = forms.ChoiceField(
                choices=[('True', 'True'), ('False', 'False')],
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        elif quiz_type == 'identification':
            self.fields['multiple_choice_options'].widget = forms.HiddenInput()  # Hide options
            self.fields['answer'].widget.attrs['placeholder'] = 'Enter correct answer'
