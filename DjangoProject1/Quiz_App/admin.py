from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Classroom, Quiz, Question, StudentQuizScore

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Classroom, Quiz, Question


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'classroom_display', 'due_date', 'created_at')
    search_fields = ('title', 'classroom__class_name')
    list_filter = ('due_date',)
    ordering = ('-created_at',)

    def classroom_display(self, obj):
        """Display the classroom associated with the quiz."""
        return f"{obj.classroom.class_name} ({obj.classroom.section})" if obj.classroom else "-"
    classroom_display.short_description = 'Classroom'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'question_text',
        'creator_display',
        'quizzes_display',
        'question_type',
        'options_display',
        'correct_answers_display',
        'true_false_display',
    )
    search_fields = ('question_text', 'quizzes__title', 'correct_answers')
    list_filter = ('question_type', 'quizzes__title', 'creator')
    ordering = ('question_text',)

    def quizzes_display(self, obj):
        """Display quizzes associated with the question."""
        quizzes = obj.quizzes.all()
        return ", ".join([quiz.title for quiz in quizzes]) if quizzes else "-"
    quizzes_display.short_description = 'Quizzes'

    def options_display(self, obj):
        """Display options as a comma-separated list."""
        options = obj.options_as_list()
        return ", ".join(options) if options else "-"
    options_display.short_description = 'Options'

    def correct_answers_display(self, obj):
        """Display correct answers as a comma-separated list."""
        correct_answers = obj.correct_answers_as_list()
        return ", ".join(correct_answers) if correct_answers else "-"
    correct_answers_display.short_description = 'Correct Answers'

    def true_false_display(self, obj):
        """Display True/False answer if applicable."""
        if obj.question_type == 'true_false':
            return obj.correct_answers if obj.correct_answers else "-"
        return "-"
    true_false_display.short_description = 'True/False Answer'

    def creator_display(self, obj):
        """Display the username of the question creator."""
        return obj.creator.username if obj.creator else "-"
    creator_display.short_description = 'Creator'

    def save_model(self, request, obj, form, change):
        """
        Automatically assign the creator to the logged-in user if the question is new.
        """
        if not obj.pk:  # If the object is new
            obj.creator = request.user
        obj.full_clean()  # Ensure all validations are respected
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Limit the creator field to teachers in the admin interface.
        """
        if db_field.name == "creator":
            kwargs["queryset"] = User.objects.filter(profile__role="teacher")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(StudentQuizScore)
class StudentQuizScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'total_questions', 'submitted_at')
    list_filter = ('quiz',)
    search_fields = ('student__username', 'quiz__title')

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



