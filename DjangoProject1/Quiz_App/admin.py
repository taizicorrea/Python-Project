from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Classroom, Quiz, Question, Choice, Submission, Answer


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('classroom_display', 'teacher_display', 'class_name', 'section', 'subject', 'room', 'class_code', 'created_at', 'enrolled_students')
    search_fields = ('class_name', 'section', 'teacher__username')  # Enable search by class name, section, and teacher username
    list_filter = ('created_at',)  # Filter by creation date
    list_per_page = 20  # Pagination: 20 items per page

    def teacher_display(self, obj):
        """Display the teacher in the format user<ID>Id."""
        return f"user{obj.teacher.id}Id"
    teacher_display.short_description = 'Teacher'  # Column name in admin list view

    def classroom_display(self, obj):
        """Display the classroom ID in the format classroom<ID>Id."""
        return f"classroom{obj.id}Id"
    classroom_display.short_description = 'Classroom ID'  # Column name in admin list view

    def enrolled_students(self, obj):
        """Return a comma-separated list of enrolled students in the format user<ID>Id."""
        return ", ".join([f"user{student.id}Id" for student in obj.students.all()])
    enrolled_students.short_description = 'Enrolled Students'


# Inline for Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


# Extend the default UserAdmin
class UserAdmin(DefaultUserAdmin):
    inlines = [ProfileInline]
    list_display = ('formatted_id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    search_fields = ('username', 'email', 'profile__role')  # Enable search by username, email, and role

    def formatted_id(self, obj):
        """Format the user ID as user<ID>Id."""
        return f"user{obj.id}Id"
    formatted_id.short_description = 'User ID'

    def get_role(self, obj):
        """Get the role of the user from the Profile model."""
        return obj.profile.role if hasattr(obj, 'profile') else None
    get_role.short_description = 'Role'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('quiz_display', 'classroom', 'title', 'scheduled_date', 'duration', 'is_published', 'created_at')
    search_fields = ('title', 'classroom__class_name')
    list_filter = ('is_published', 'scheduled_date')
    filter_horizontal = ('reused_questions',)  # Allows selecting existing questions in a horizontal filter widget

    def quiz_display(self, obj):
        """Display the quiz ID in the format quiz<ID>Id."""
        return f"quiz{obj.id}Id"
    quiz_display.short_description = 'Quiz ID'


# Inline for Choices in QuestionAdmin
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1  # Allow adding one new blank row
    fields = ('choice_text', 'is_correct')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_display', 'question_text', 'quiz', 'question_type', 'points')  # Added question_text
    search_fields = ('question_text', 'quiz__title')  # Enable search by question text and quiz title
    list_filter = ('question_type',)  # Filter by question type
    inlines = [ChoiceInline]  # Inline for managing choices in questions
    list_per_page = 20  # Pagination

    def question_display(self, obj):
        """Display the question ID in the format question<ID>Id."""
        return f"question{obj.id}Id"
    question_display.short_description = 'Question ID'



# Inline for Answers in SubmissionAdmin
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0  # Remove extra blank rows
    fields = ('question', 'selected_choice')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_display', 'student', 'quiz', 'submitted_at', 'score')
    search_fields = ('student__username', 'quiz__title')  # Enable search by student username and quiz title
    list_filter = ('submitted_at',)  # Filter by submission date
    inlines = [AnswerInline]  # Inline for managing answers in submissions
    list_per_page = 20  # Pagination

    def submission_display(self, obj):
        """Display the submission ID in the format submission<ID>Id."""
        return f"submission{obj.id}Id"
    submission_display.short_description = 'Submission ID'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_display', 'submission', 'question', 'selected_choice')
    search_fields = ('submission__student__username', 'question__question_text')  # Enable search by student username and question text
    list_per_page = 20  # Pagination

    def answer_display(self, obj):
        """Display the answer ID in the format answer<ID>Id."""
        return f"answer{obj.id}Id"
    answer_display.short_description = 'Answer ID'
