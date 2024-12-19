from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Classroom, Quiz, Question



@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'classroom_display', 'quiz_type', 'due_date', 'created_at')
    search_fields = ('title', 'classroom__class_name', 'quiz_type')
    list_filter = ('quiz_type', 'due_date')
    ordering = ('-created_at',)

    def classroom_display(self, obj):
        """Display the classroom associated with the quiz."""
        return f"{obj.classroom.class_name} ({obj.classroom.section})"
    classroom_display.short_description = 'Classroom'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quizzes_display', 'question_type', 'options_display', 'correct_answers_display')
    search_fields = ('question_text', 'quizzes__title', 'correct_answers')
    list_filter = ('question_type', 'quizzes__title')
    ordering = ('question_text',)

    def quizzes_display(self, obj):
        """Display the quizzes associated with the question as a comma-separated list."""
        return ", ".join([quiz.title for quiz in obj.quizzes.all()])
    quizzes_display.short_description = 'Quizzes'

    def options_display(self, obj):
        """Display options as a comma-separated list."""
        return ", ".join(obj.options_as_list()) if obj.options_as_list() else "-"
    options_display.short_description = 'Options'

    def correct_answers_display(self, obj):
        """Display correct answers as a comma-separated list."""
        return ", ".join(obj.correct_answers_as_list()) if obj.correct_answers_as_list() else "-"
    correct_answers_display.short_description = 'Correct Answers'

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('classroom_display', 'teacher_display', 'class_name', 'section', 'subject', 'room', 'class_code', 'created_at', 'enrolled_students')  # Include 'enrolled_students'

    def teacher_display(self, obj):
        # Custom format: user<ID>Id
        return f"user{obj.teacher.id}Id"
    teacher_display.short_description = 'Teacher'  # Optional: To change the column name in the admin list view

    def classroom_display(self, obj):
        # Format the id as "classroom<ID>Id"
        return f"classroom{obj.id}Id"
    classroom_display.short_description = 'Classroom ID'  # Optional: To change the column name in admin

    def enrolled_students(self, obj):
        # Return a comma-separated list of user IDs (user<ID>Id format)
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

    def formatted_id(self, obj):
        return f"user{obj.id}Id"  # Format the ID as "user1Id", "user2Id", etc.
    formatted_id.short_description = 'User ID'

    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else None
    get_role.short_description = 'Role'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)



