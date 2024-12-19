import random
import json
import string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.urls import reverse

from .forms import CustomAuthenticationForm, QuizForm, SignupForm, JoinClassForm, CreateClassForm, ProfileForm, \
    PasswordChangeForm, AddStudentForm, QuestionForm, EditClassroomForm
from django.contrib.auth import logout
from django.contrib import messages
from .models import Classroom, Quiz, Question

#Sign Up View
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user
            messages.success(request, "Signup successful! Welcome!")
            return redirect('landing')  # Redirect to landing page
    else:
        form = SignupForm()
    return render(request, 'Quiz_App/signup.html', {'form': form})

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('landing')  # Already logged in

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['has_logged_in'] = True

            # Check if the user is a superuser (admin)
            if user.is_superuser:
                return redirect('/admin/')  # Redirect admin to Django admin panel
            else:
                return redirect('landing')  # Redirect normal users to landing page
        else:
            form.add_error(None, "Invalid username/email or password.")
    else:
        form = CustomAuthenticationForm()

    response = render(request, 'Quiz_App/login.html', {'form': form})
    response['Cache-Control'] = 'no-store'
    return response


# Add Student in a Classroom
def add_student(request):
    if request.method == "POST":
        classroom_id = request.POST.get('classroom_id')
        print("Classroom ID from POST:", classroom_id)  # Debugging: Check the classroom ID

        form = AddStudentForm(request.POST)
        if form.is_valid():
            classroom = get_object_or_404(Classroom, id=classroom_id)

            student_email_or_username = form.cleaned_data['email_or_username']

            try:
                student = User.objects.get(email=student_email_or_username)
            except User.DoesNotExist:
                try:
                    student = User.objects.get(username=student_email_or_username)
                except User.DoesNotExist:
                    messages.error(request, "Student not found.")
                    return redirect('landing')  # Redirect to landing without classroom_id

            classroom.students.add(student)
            classroom.save()

            messages.success(request,f"Student {student.first_name} {student.last_name} has been added to the classroom.")

            # Redirect to the same page but include the classroom_id in the query string
            return HttpResponseRedirect(f"{reverse('landing')}?classroom_id={classroom.id}")

        else:
            messages.error(request, "Form is not valid.")
            return redirect('landing')  # Redirect to landing without classroom_id
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


def remove_student(request):
    if request.method == "POST":
        classroom_id = request.POST.get('classroom_id')
        student_id = request.POST.get('student_id')

        classroom = get_object_or_404(Classroom, id=classroom_id)
        student = get_object_or_404(User, id=student_id)

        # Remove the student from the classroom
        classroom.students.remove(student)

        messages.success(request, f"{student.first_name} {student.last_name} has been removed from the classroom.")
        return redirect(f'{reverse("landing")}?classroom_id={classroom.id}')
    else:
        return redirect('landing')

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
                    messages.warning(request, "You are already enrolled in this classroom.")
                else:
                    # Add the user to the students list
                    classroom.students.add(request.user)
                    messages.success(request, f"You have successfully joined the class: {classroom.class_name}")

                return redirect('landing')  # Redirect to landing page or classroom list

            except Classroom.DoesNotExist:
                messages.error(request, "Invalid class code. Please try again.")

        else:
            messages.error(request, "Invalid input. Please ensure the class code is correct.")

        return redirect('landing') # Redirect back to the form page for retry

    else:
        form = JoinClassForm()
    return render(request, 'Quiz_App/landing_page.html', {'form': form})


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

@login_required
def landing_page(request):
    classrooms = []
    quizzes = []
    selected_classroom = None

    if request.user.is_authenticated:
        # Fetch classrooms based on user's role
        if request.user.profile.role == 'teacher':
            classrooms = Classroom.objects.filter(teacher=request.user).prefetch_related('students')
        elif request.user.profile.role == 'student':
            classrooms = request.user.classrooms.all().prefetch_related('students')

        # Fetch selected classroom details based on query parameter
        classroom_id = request.GET.get('classroom_id')
        if classroom_id:
            selected_classroom = get_object_or_404(Classroom, id=classroom_id)
            quizzes = Quiz.objects.filter(classroom=selected_classroom).order_by('due_date')  # Quizzes for selected classroom

    join_form = JoinClassForm()
    create_form = CreateClassForm()
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm()
    add_student = AddStudentForm()
    edit_classroom = EditClassroomForm()

    return render(request, 'Quiz_App/landing_page.html', {
        'classrooms': classrooms,
        'selected_classroom': selected_classroom,  # Pass selected classroom
        'quizzes': quizzes,  # Pass quizzes for the selected classroom
        'join_form': join_form,
        'create_form': create_form,
        'edit_classroom': edit_classroom,
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
    return render(request, 'landing_page.html')


def create_quiz(request, classroom_id):
    # Restrict access to teachers
    if request.user.profile.role != 'teacher':
        messages.error(request, "You are not authorized to create a quiz.")
        return redirect('landing')

    classroom = get_object_or_404(Classroom, id=classroom_id)

    if request.method == 'POST':
        form = QuizForm(request.POST)

        try:
            # Parse questions data from JSON
            questions_data = json.loads(request.POST.get('questions', '[]'))
            print("Received questions data:", questions_data)  # Debug log
        except json.JSONDecodeError:
            messages.error(request, "Invalid questions data format.")
            return redirect('create_quiz', classroom_id=classroom.id)

        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.classroom = classroom
            quiz.save()

            for question in questions_data:
                # Check if the ID is numeric (existing question)
                if isinstance(question['id'], int):
                    try:
                        existing_question = Question.objects.get(id=question['id'])
                        quiz.questions.add(existing_question)
                    except Question.DoesNotExist:
                        messages.error(request, f"Question with ID {question['id']} does not exist.")
                        continue

                # Check if the ID is a string starting with "temp-" (new question)
                elif isinstance(question['id'], str) and question['id'].startswith('temp-'):
                    new_question = Question.objects.create(
                        question_text=question['question_text'],
                        question_type=question.get('question_type', 'multiple_choice'),
                        multiple_choice_options="\n".join(question.get('multiple_choice_options', [])),
                        correct_answers="\n".join(question.get('correct_answer', [])),
                    )
                    quiz.questions.add(new_question)

                else:
                    messages.error(request, "Invalid question data format.")
                    continue

            messages.success(request, "Quiz and questions created successfully!")
            return redirect(f'{reverse("landing")}?classroom_id={classroom.id}')
        else:
            print("Form errors:", form.errors)  # Debug log
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = QuizForm()

    return render(request, 'Quiz_App/create_quiz.html', {'form': form, 'classroom': classroom})


def get_questions(request):
    if request.method == 'GET':
        try:
            # Retrieve all questions with the required fields
            questions = list(
                Question.objects.values('id', 'question_text', 'question_type', 'multiple_choice_options', 'correct_answers')
            )

            # Process multiple choice options and correct answers
            for question in questions:
                question['multiple_choice_options'] = question['multiple_choice_options'].split("\n") if question['multiple_choice_options'] else []
                question['correct_answers'] = question['correct_answers'].split("\n") if question['correct_answers'] else []

            # Return the questions as JSON
            return JsonResponse({'questions': questions}, status=200)

        except Exception as e:
            # Log and return an error response
            print(f"Error retrieving questions: {str(e)}")
            return JsonResponse({'error': 'Failed to retrieve questions.'}, status=500)
    else:
        # Handle non-GET requests
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
def reset_quiz_session(request):
    """
    Resets the session data for a quiz under creation.
    """
    if 'quiz_data' in request.session:
        del request.session['quiz_data']
    messages.success(request, "Quiz session reset successfully.")
    return redirect('create_quiz', classroom_id=request.GET.get('classroom_id'))

@login_required
def add_question(request):
    """
    Fetch existing questions from the database for reuse.
    """
    if request.method == 'GET':
        questions = list(Question.objects.values('id', 'question_text', 'question_type'))
        return JsonResponse({'questions': questions})
