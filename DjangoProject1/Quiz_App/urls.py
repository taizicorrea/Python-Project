# Quiz_App/urls.py
from django.urls import path
from . import views
from .views import signup_view, login_view, landing_page, logout_view, profile_view, join_class, \
    create_class, account_management, get_classroom_students, add_student, unenroll_student, delete_classroom

urlpatterns = [
    # path('', home_view, name='home'),
    path('', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('landing/', landing_page, name='landing'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('join-class/', join_class, name='join_class'),
    path('create-class/', create_class, name='create_class'),  # Add the new route
    path('account_management/', account_management, name='account_management'),
    path('add_student/', add_student, name='add_student'),

    path('classroom/delete/<int:classroom_id>/', delete_classroom, name='delete_classroom'),
    path('create-quiz/<int:classroom_id>/', views.create_quiz, name='create_quiz'),
    path('fetch-reusable-questions/', views.fetch_reusable_questions, name='fetch_reusable_questions'),
    path('quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('unenroll/<int:classroom_id>/', unenroll_student, name='unenroll_student'),
    path('classroom/<int:classroom_id>/students', get_classroom_students, name='get_classroom_students'),
]
