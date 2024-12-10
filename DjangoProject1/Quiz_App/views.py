import random
import string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from .forms import CustomAuthenticationForm, SignupForm, JoinClassForm, CreateClassForm, ProfileForm, \
    PasswordChangeForm, AddStudentForm
from django.contrib.auth import logout
from django.contrib import messages
from .models import Classroom, Profile


def home_view(request):
    classrooms = []
    if request.user.is_authenticated:
        # Check user role
        print(request.user.profile.role)  # Debugging line
        if request.user.profile.role == 'teacher':
            classrooms = Classroom.objects.filter(teacher=request.user)
    return render(request, 'Quiz_App/landing_page.html', {'classrooms': classrooms})

def add_student(request):
    if request.method == 'POST':
        form = AddStudentForm(request.POST)
        if form.is_valid():
            email_or_username = form.cleaned_data['email_or_username']
            # Add logic here (e.g., check if the user exists or create a new user)
            return redirect('landing')  # Replace with your actual redirect
    else:
        form = AddStudentForm()

    return render(request, 'landing_page.html', {'form': form})  # Make sure this matches the template filename


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            messages.success(request, "Signup successful!")  # Add a success message
            return redirect('login')  # Redirect to the login page
    else:
        form = SignupForm()
    return render(request, 'Quiz_App/signup.html', {'form': form})


# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('landing')  # Redirect to landing if already logged in

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['has_logged_in'] = True  # Set session variable
            return redirect('landing')
        else:
            form.add_error(None, " Invalid username/email or password. ")  # Adjust error message
    else:
        form = CustomAuthenticationForm()

    response = render(request, 'Quiz_App/login.html', {'form': form})

    # Prevent caching of the login page
    response['Cache-Control'] = 'no-store'

    return response


# Profile Management Update in Credentials
@login_required
def account_management(request):
    user = request.user
    profile_form = ProfileForm(instance=user)
    password_form = PasswordChangeForm()

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('landing')
            else:
                messages.error(request, 'Failed to update profile. Please try again.')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                if user.check_password(password_form.cleaned_data['current_password']):
                    user.set_password(password_form.cleaned_data['new_password'])
                    user.save()
                    messages.success(request, 'Password updated successfully!')
                    update_session_auth_hash(request, user)  # Keeps the user logged in
                    return redirect('landing')
                else:
                    messages.error(request, 'Failed to update password. Please try again.')
                    password_form.add_error('current_password', 'Current password is incorrect.')

        elif 'delete_account' in request.POST:
            # Logic for deleting the user's account
            user.delete()
            logout(request)  # Log the user out after account deletion
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('landing')  # Redirect to the homepage or another appropriate pag

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'landing_page.html', context)


def join_class(request):
    if request.method == 'POST':
        form = JoinClassForm(request.POST)
        if form.is_valid():
            class_code = form.cleaned_data['class_code']

            try:
                # Try to get the Classroom object based on the class_code
                classroom = Classroom.objects.get(class_code=class_code)

                # Check if the user is already enrolled in the classroom
                if request.user in classroom.students.all():
                    messages.error(request, "You are already enrolled in this classroom.")
                    return redirect('landing')  # Redirect back to the landing page (or wherever you want)

                # Add the user to the students list
                classroom.students.add(request.user)
                messages.success(request,
                                 f"You have successfully joined the class: {classroom.class_name}")  # Use class_name instead of class_code
                return redirect('landing')  # Redirect to the desired page

            except Classroom.DoesNotExist:
                messages.error(request, "Invalid class code.")
                return redirect('landing')  # Redirect back if class code is invalid
        else:
            messages.error(request, "Invalid form submission.")
            return redirect('landing')  # Redirect back if the form is not valid
    else:
        form = JoinClassForm()  # Empty form for GET request
    return render(request, 'landing_page.html', {'form': form})


def generate_class_code(length=7):
    characters = string.ascii_letters + string.digits  # Letters (both uppercase and lowercase) and digits
    return ''.join(random.choice(characters) for _ in range(length))

@login_required
def create_class(request):
    if request.method == 'POST':
        form = CreateClassForm(request.POST)
        if form.is_valid():
            # Extract form data
            class_name = form.cleaned_data['class_name']
            section = form.cleaned_data['section']
            subject = form.cleaned_data['subject']
            room = form.cleaned_data['room']

            # Generate a random class code
            class_code = generate_class_code()

            # Create new class and save to the database
            classroom = Classroom.objects.create(
                teacher=request.user,  # Automatically uses the primary key (user.id)
                class_name=class_name,
                section=section,
                subject=subject,
                room=room,
                class_code=class_code  # Save the generated class code
            )

            messages.success(request, f"Class '{class_name}' created successfully with code: {class_code}!")
            return redirect('landing')  # Redirect to your landing page or dashboard
        else:
            messages.error(request, "There was an error creating the class.")
    else:
        form = CreateClassForm()  # Empty form for GET request

    return render(request, 'landing_page.html', {'form': form})

def home(request):
    # Check if the user is logged in
    if request.user.is_authenticated:
        # If the user is logged in, redirect to the landing page
        return redirect('landing')  # Replace 'landing' with your actual landing page URL name
    else:
        # If not logged in, render the home page
        return render(request, 'home.html')

def get_classroom_students(request, classroom_id):
    try:
        classroom = Classroom.objects.get(id=classroom_id)
        students = classroom.students.all()
        student_data = [
            {"first_name": student.first_name, "last_name": student.last_name}
            for student in students
        ]
        return JsonResponse({"students": student_data})
    except Classroom.DoesNotExist:
        return JsonResponse({"error": "Classroom not found"}, status=404)

# Landing page view
@login_required
def landing_page(request):
    classrooms = []
    if request.user.is_authenticated:
        if request.user.profile.role == 'teacher':
            classrooms = Classroom.objects.filter(teacher=request.user).prefetch_related('students')
        elif request.user.profile.role == 'student':
            classrooms = request.user.classrooms.all().prefetch_related('students')

    join_form = JoinClassForm()
    create_form = CreateClassForm()
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm()
    add_student = AddStudentForm()

    return render(request, 'Quiz_App/landing_page.html', {
        'classrooms': classrooms,
        'join_form': join_form,
        'create_form': create_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'add_student': add_student,
    })

# Home page view
def home_view(request):
    return render(request, 'Quiz_App/home.html')

# Logout view
def logout_view(request):
    logout(request)
    response = redirect('login')
    response['Cache-Control'] = 'no-store'  # Prevent caching of the page
    return response

def profile_view(request):
    return render(request, 'Quiz_App/profile_management.html')
