import random
import string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CustomAuthenticationForm, SignupForm, JoinClassForm, CreateClassForm, ProfileForm, \
    PasswordChangeForm, AddStudentForm, EditClassroomForm
from django.contrib.auth import logout
from django.contrib import messages
from .models import Classroom

#Sign Up View
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user to the database
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

# Add Student in a Classroom
def add_student(request):
    if request.method == "POST":
        form = AddStudentForm(request.POST)
        if form.is_valid():
            classroom_id = request.POST.get('classroom_id')
            classroom = get_object_or_404(Classroom, id=classroom_id)
            student_email_or_username = form.cleaned_data['email_or_username']

            try:
                # Try to get the student by email
                student = User.objects.get(email=student_email_or_username)
            except User.DoesNotExist:
                try:
                    # If not found by email, try by username
                    student = User.objects.get(username=student_email_or_username)
                except User.DoesNotExist:
                    # If no student found, show error message
                    messages.error(request, "Student not found.")
                    return redirect('landing')  # Redirect to the page where you want to show the message

            # Add the student to the classroom
            classroom.students.add(student)
            classroom.save()

            # Show success message
            messages.success(request, f"Student {student} has been added to the classroom.")

            return redirect('landing')  # Redirect to the appropriate page (e.g., classroom page)
        else:
            messages.error(request, "Form is not valid.")
            return redirect('landing')  # Redirect to the form page

    else:
        form = AddStudentForm()

    return render(request, 'landing_page.html', {'add_student': form})

# Uneroll student from the classroom
def unenroll_student(request, classroom_id):
    # Get the classroom and the current user (student)
    classroom = get_object_or_404(Classroom, id=classroom_id)
    user = request.user

    if user.profile.role == 'student':
        # Handle confirmation form submission
        if request.method == "POST":
            # Remove the student from the classroom
            classroom.students.remove(user)
            messages.success(request, 'You have successfully unenrolled from the classroom.')
            return redirect('landing')  # Redirect to another page (e.g., landing or classroom list)

        # Render the confirmation page if the method is GET
        return render(request, 'confirm_unenroll.html', {'classroom': classroom})

    else:
        messages.error(request, 'You are not authorized to unenroll from this classroom.')
        return HttpResponseForbidden("You are not authorized to unenroll from this classroom.")

#Remove the student from the classroom, Using teacher role.
def delete_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, 'Classroom deleted successfully.')
        return redirect('landing')  # Update this to the name of your classroom list view
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('landing')  # Update this to the name of your classroom list view

# Profile Management Update in Credentials
@login_required
def account_management(request):
    user = request.user

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.error(request, 'Failed to update profile. Please try again.')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                current_password = password_form.cleaned_data['current_password']
                new_password = password_form.cleaned_data['new_password']
                reenter_password = password_form.cleaned_data['confirm_password']

                # Check if the current password is correct
                if user.check_password(current_password):
                    # Check if new password and re-entered password match
                    if new_password == reenter_password:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'Password updated successfully!')
                        update_session_auth_hash(request, user)
                    else:
                        messages.error(request, 'The new passwords do not match.')
                else:
                    messages.error(request, 'Current password is incorrect.')

        elif 'delete_account' in request.POST:
            user.delete()
            logout(request)
            messages.success(request, 'Your account has been deleted successfully.')

    # Redirect to landing if accessed via GET or invalid POST
    return redirect('landing')


# Join Cass View
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


# View for Generate Class Code in Classroom
def generate_class_code(length=7):
    characters = string.ascii_letters + string.digits  # Letters (both uppercase and lowercase) and digits
    return ''.join(random.choice(characters) for _ in range(length))

# View for Create Class in Teacher Role
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

            messages.success(request, f"Class '{class_name}' created successfully!")
            return redirect('landing')  # Redirect to your landing page or dashboard
        else:
            messages.error(request, "There was an error creating the class.")
    else:
        form = CreateClassForm()  # Empty form for GET request

    return render(request, 'landing_page.html', {'form': form})


# Process to get the Students and Teacher in People Tab.
def get_classroom_students(request, classroom_id):
    try:
        classroom = Classroom.objects.get(id=classroom_id)
        students = classroom.students.all()
        teacher = classroom.teacher

        current_user = 'teacher' if request.user == teacher else 'student'

        student_data = [
            {"first_name": student.first_name, "last_name": student.last_name}
            for student in students
        ]

        teacher_data = {
            "id": teacher.id,
            "first_name": teacher.first_name,
            "last_name": teacher.last_name
        }

        return JsonResponse({
            "teacher": teacher_data,
            "students": student_data,
            "current_user": current_user,
        })

    except Classroom.DoesNotExist:
        return JsonResponse({"error": "Classroom not found"}, status=404)

# Edit Classroom in Details
def edit_classroom(request):
    if request.method == 'POST':
        classroom_id = request.POST.get('modal-classroom-id')  # Get the classroom ID from the hidden field
        classroom = get_object_or_404(Classroom, id=classroom_id)  # Get the classroom instance
        form = EditClassroomForm(request.POST, instance=classroom)  # Populate form with data

        if form.is_valid():
            form.save()  # Save the updated classroom
            messages.success(request, 'Classroom updated successfully!')
            return redirect('landing')  # Redirect to the same page and show the updated classroom details
        else:
            # If there are form errors, print them (optional) and show an error message
            print(form.errors)  # Optional: for debugging form errors
            messages.error(request, 'There was an error updating the classroom.')
            return redirect('landing')  # Redirect to the same page and show the updated classroom details
    else:
        # If it's a GET request, display the form
        form = EditClassroomForm()

    return render(request, 'Quiz_App/landing_page.html', {
        'form': form,
    })

# Landing page view
@login_required
def landing_page(request):
    classrooms = []
    selected_classroom = None

    if request.user.is_authenticated:
        if request.user.profile.role == 'teacher':
            classrooms = Classroom.objects.filter(teacher=request.user).prefetch_related('students')
        elif request.user.profile.role == 'student':
            classrooms = request.user.classrooms.all().prefetch_related('students')

    # Check if a classroom ID is provided to show its details
    classroom_id = request.GET.get('classroom_id')
    if classroom_id:
        selected_classroom = get_object_or_404(Classroom, id=classroom_id)

    # Check if a classroom ID is provided to show its details
    classroom_id = request.GET.get('classroom_id')
    if classroom_id:
        selected_classroom = get_object_or_404(Classroom, id=classroom_id)

    join_form = JoinClassForm()
    create_form = CreateClassForm()
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm()
    add_student = AddStudentForm()
    edit_classroom = EditClassroomForm()

    return render(request, 'Quiz_App/landing_page.html', {
        'classrooms': classrooms,
        'join_form': join_form,
        'create_form': create_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'add_student': add_student,
        'selected_classroom': selected_classroom,  # Pass selected classroom to template
        'edit_classroom': edit_classroom,
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
    return render(request, 'landing_page.html')
