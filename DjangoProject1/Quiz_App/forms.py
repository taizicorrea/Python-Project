from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile

class SignupForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name', 'aria-label': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name', 'aria-label': 'Last Name'})
    )
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username', 'aria-label': 'Username'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email', 'aria-label': 'Email'})
    )
    role = forms.ChoiceField(
        choices=[('', 'Select your role'), ('student', 'Student'), ('teacher', 'Teacher')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'aria-label': 'Role'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password', 'aria-label': 'Password'}),
        required=True
    )
    reenter_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter your password', 'aria-label': 'Re-enter Password'}),
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
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
            # Save the Profile with the selected role
            role = self.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
            user_id = user.id  # Access the primary key of the user
            print("User ID:", user_id)  # You can log it or use it as needed
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

