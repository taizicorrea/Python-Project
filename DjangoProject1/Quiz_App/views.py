import csv
import random
import json
import string
from io import BytesIO

from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.urls import reverse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
from django.templatetags.static import static

from .forms import CustomAuthenticationForm, QuizForm, SignupForm, JoinClassForm, CreateClassForm, ProfileForm, \
    PasswordChangeForm, AddStudentForm, QuestionForm, EditClassroomForm, EditQuestionForm
from django.contrib.auth import logout
from django.contrib import messages
from .models import Classroom, Quiz, Question, StudentQuizScore


#Sign Up View
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Set the backend for the user manually
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            # Log in the user
            login(request, user)

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

            if request.user.profile.role == 'teacher':
                # Fetch all quizzes for teachers
                quizzes = Quiz.objects.filter(classroom=selected_classroom).order_by('due_date')
            elif request.user.profile.role == 'student':
                # Fetch only active quizzes for students
                quizzes = Quiz.objects.filter(classroom=selected_classroom, is_active=True).order_by('due_date')

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


@login_required
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

            linked_existing_questions = []
            created_new_questions = []

            for question in questions_data:
                try:
                    # Process existing questions
                    if 'id' in question and isinstance(question['id'], int):
                        existing_question = Question.objects.get(id=question['id'])
                        quiz.questions.add(existing_question)
                        linked_existing_questions.append(existing_question.id)
                        print(f"Linked existing question ID {existing_question.id} to quiz ID {quiz.id}.")

                    # Process new questions
                    elif 'id' in question and isinstance(question['id'], str) and question['id'].startswith('temp-'):
                        new_question = Question.objects.create(
                            question_text=question['question_text'],
                            question_type=question.get('question_type', 'multiple_choice'),
                            multiple_choice_options="\n".join(question.get('multiple_choice_options', [])),
                            correct_answers="\n".join(question.get('correct_answers', [])),
                        )
                        quiz.questions.add(new_question)
                        created_new_questions.append(new_question.id)
                        print(f"New question '{new_question.question_text}' created and linked to quiz ID {quiz.id}.")

                except Question.DoesNotExist:
                    messages.error(request, f"Question with ID {question['id']} does not exist.")
                except Exception as e:
                    messages.error(request, f"Failed to process question: {e}")

            print("Linked existing questions:", linked_existing_questions)
            print("Created new questions:", created_new_questions)

            messages.success(request, "Quiz and questions created successfully!")
            return redirect(f'{reverse("landing")}?classroom_id={classroom.id}')
        else:
            print("Form errors:", form.errors)  # Debug log
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = QuizForm()

    return render(request, 'Quiz_App/create_quiz.html', {'form': form, 'classroom': classroom})


# Fetch All Questions
@login_required
def get_questions(request):
    if request.method == 'GET':
        questions = list(
            Question.objects.values('id', 'question_text', 'question_type', 'multiple_choice_options', 'correct_answers')
        )
        for question in questions:
            question['multiple_choice_options'] = question['multiple_choice_options'].split("\n") if question['multiple_choice_options'] else []
            question['correct_answers'] = question['correct_answers'].split("\n") if question['correct_answers'] else []
        return JsonResponse({'questions': questions}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# Reset Quiz Session
@login_required
def reset_quiz_session(request):
    if 'quiz_data' in request.session:
        del request.session['quiz_data']
    messages.success(request, "Quiz session reset successfully.")
    return redirect('create_quiz', classroom_id=request.GET.get('classroom_id'))

@login_required
def add_question(request):
    if request.method == 'GET':
        questions = list(
            Question.objects.values('id', 'question_text', 'question_type', 'multiple_choice_options', 'correct_answers')
        )
        for question in questions:
            question['multiple_choice_options'] = (
                question['multiple_choice_options'].split("\n") if question['multiple_choice_options'] else []
            )
            question['correct_answers'] = (
                question['correct_answers'].split("\n") if question['correct_answers'] else []
            )

        return JsonResponse({'questions': questions}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = EditQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('edit_quiz', quiz_id=question.quizzes.first().id)  # Assuming a question belongs to one quiz
    else:
        form = EditQuestionForm(instance=question)

    return render(request, 'Quiz_App/edit_question.html', {'form': form, 'question': question})

def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quizzes.first().id
    question.delete()
    return redirect('edit_quiz', quiz_id=quiz_id)

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Ensure the student is enrolled in the classroom
    if request.user not in quiz.classroom.students.all():
        messages.error(request, "You are not enrolled in this classroom.")
        return redirect('landing')

    # Check if the quiz is active and not past the due date
    if not quiz.is_active:
        messages.error(request, "This quiz is currently disabled.")
        return redirect('landing')

    if quiz.due_date < now():  # Use Django's timezone-aware now
        messages.error(request, "This quiz is no longer available.")
        return redirect('landing')

    if request.method == 'GET':
        questions = quiz.questions.all()
        return render(request, 'Quiz_App/take_quiz.html', {
            'quiz': quiz,
            'questions': questions
        })

    elif request.method == 'POST':
        # Redirect POST requests to the `submit_quiz` view
        return submit_quiz(request, quiz_id)

    # If the request method is neither GET nor POST, return an error
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Ensure the student is enrolled in the classroom
    if request.user not in quiz.classroom.students.all():
        messages.error(request, "You are not enrolled in this classroom.")
        return redirect('landing')

    if request.method == 'POST':
        answers = request.POST.dict()
        feedback = []  # Store feedback for each question
        score = 0
        total = quiz.questions.count()

        # Iterate through each question in the quiz
        for question in quiz.questions.all():
            user_answer = answers.get(f"question_{question.id}", "").strip()
            correct_answers = question.correct_answers_as_list()

            is_correct = user_answer in correct_answers
            if is_correct:
                score += 1

            # Append feedback for this question
            feedback.append({
                "question": question.question_text,
                "user_answer": user_answer,
                "correct_answers": correct_answers,
                "is_correct": is_correct,
            })

        # Save the student's score
        StudentQuizScore.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            total_questions=total
        )

        # Render the feedback page
        return render(request, 'Quiz_App/quiz_feedback.html', {
            'quiz': quiz,
            'feedback': feedback,
            'score': score,
            'total': total,
        })

    # Return an error if the method is not POST
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
def get_quiz_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'GET':
        questions = list(
            quiz.questions.values(
                'id', 'question_text', 'question_type', 'multiple_choice_options'
            )
        )
        for question in questions:
            question['multiple_choice_options'] = (
                question['multiple_choice_options'].split("\n")
                if question['multiple_choice_options'] else []
            )
        return JsonResponse({'questions': questions}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



@login_required
def download_teacher_quiz_report_pdf(request, quiz_id):
    # Fetch the quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Check if the logged-in user is the teacher of the class
    if request.user != quiz.classroom.teacher:
        messages.error(request, "You are not authorized to download this report.")
        return redirect('landing')

    # Fetch student scores for the quiz
    student_scores = StudentQuizScore.objects.filter(quiz=quiz)

    # Handle case where no scores exist
    if not student_scores.exists():
        messages.error(request, "No responses found for this quiz.")
        return redirect('landing')

    # Prepare the student data for the report
    student_data = [
        {
            'student_name': f"{score.student.first_name} {score.student.last_name}",
            'score': score.score,
            'total_questions': score.total_questions,
            'percentage': round((score.score / score.total_questions) * 100, 2) if score.total_questions > 0 else 0,
        }
        for score in student_scores
    ]

    # Context for the PDF
    context = {
        'subject': quiz.classroom.subject,
        'quiz_title': quiz.title,
        'teacher': f'{quiz.classroom.teacher.first_name} {quiz.classroom.teacher.last_name}',
        'date_printed': now().strftime('%d/%m/%Y %I:%M %p'),
        'student_data': student_data,
    }

    # Render the template to HTML
    html_content = render_to_string('Quiz_App/teacher_quiz_report_template.html', context)

    # Generate the PDF using WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{quiz.classroom.subject}_{quiz.title}_teacher_report.pdf"'

    # Convert HTML content to PDF
    HTML(string=html_content).write_pdf(response)

    return response


@login_required
def manage_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Ensure only the teacher who created the quiz can access this page
    if request.user != quiz.classroom.teacher:
        return HttpResponseForbidden("You are not authorized to manage this quiz.")

    # Handle form actions
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "disable":
            quiz.is_active = False
            quiz.save()
            messages.success(request, "Quiz has been disabled.")
        elif action == "enable":
            quiz.is_active = True
            quiz.save()
            messages.success(request, "Quiz has been enabled.")
        elif action == "delete":
            quiz.delete()
            messages.success(request, "Quiz has been deleted.")
            return redirect("landing")

    # Fetch student scores
    student_scores = []
    scores_queryset = StudentQuizScore.objects.filter(quiz=quiz)
    for score in scores_queryset:
        percentage = (score.score / score.total_questions) * 100 if score.total_questions > 0 else 0
        student_scores.append({
            "student": score.student,
            "score": score.score,
            "total_questions": score.total_questions,
            "percentage": round(percentage, 2),
        })

    # Calculate quiz-level analytics
    total_scores = [score['score'] for score in student_scores]
    total_participants = len(student_scores)
    average_score = sum(total_scores) / total_participants if total_participants > 0 else 0
    highest_score = max(total_scores, default=0)
    lowest_score = min(total_scores, default=0)

    # Calculate per-question analytics
    questions = quiz.questions.all()
    for question in questions:
        correct_responses = question.responses.filter(is_correct=True).count()
        incorrect_responses = question.responses.filter(is_correct=False).count()
        total_responses = correct_responses + incorrect_responses

        # Debugging logs
        print(f"Question: {question.question_text}")
        print(f"Correct: {correct_responses}, Incorrect: {incorrect_responses}, Total: {total_responses}")

        question.correct_answers = correct_responses
        question.incorrect_answers = incorrect_responses
        question.success_rate = (correct_responses / total_responses * 100) if total_responses > 0 else 0

    return render(request, "Quiz_App/manage_quiz.html", {
        "quiz": quiz,
        "student_scores": student_scores,
        "questions": questions,
        "quiz_analytics": {
            "average_score": round(average_score, 2),
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "total_participants": total_participants,
        },
    })



@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Ensure only the teacher who created the quiz can edit it
    if request.user != quiz.classroom.teacher:
        return HttpResponseForbidden("You are not allowed to edit this quiz.")

    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, "Quiz updated successfully.")
            return redirect('manage_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'Quiz_App/edit_quiz.html', {'form': form, 'quiz': quiz})

@csrf_exempt
def save_question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quiz_id = data.get('quizId')
            question_id = data.get('questionId')
            question_text = data.get('question_text')
            question_type = data.get('question_type')
            options = data.get('options', [])
            correct_answers = data.get('correct_answers', '')

            if not quiz_id or not question_text or not question_type:
                return JsonResponse({'success': False, 'error': 'Required fields are missing'}, status=400)

            quiz = Quiz.objects.get(id=quiz_id)

            if question_id:  # Update existing question
                question = Question.objects.get(id=question_id)
                question.question_text = question_text
                question.question_type = question_type
                question.multiple_choice_options = "\n".join(options) if options else ""
                question.correct_answers = correct_answers
                question.save()
            else:  # Create a new question
                question = Question.objects.create(
                    question_text=question_text,
                    question_type=question_type,
                    multiple_choice_options="\n".join(options) if options else "",
                    correct_answers=correct_answers,
                )
                question.quizzes.add(quiz)  # Associate the question with the quiz

            return JsonResponse({'success': True})
        except Quiz.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Quiz not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
