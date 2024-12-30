from django.urls import path, include
from . import views
from .views import signup_view, login_view, landing_page, logout_view, profile_view, join_class, \
    create_class, account_management, unenroll_student, delete_classroom, \
    edit_classroom, add_existing_questions, search_students, add_students, set_role_password
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('landing/', landing_page, name='landing'),
    path('landing/', views.landing_page, name='landing_page'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('join-class/', join_class, name='join_class'),
    path('create-class/', create_class, name='create_class'),  # Add the new route
    path('account_management/', account_management, name='account_management'),
    path('search_students/', search_students, name='search_students'),
    path('add_students/', add_students, name='add_students'),
    path('edit_classroom/', edit_classroom, name='edit_classroom'),
    path('remove_student/', views.remove_student, name='remove_student'),
    path('classroom/delete/<int:classroom_id>/', delete_classroom, name='delete_classroom'),
    path('create-quiz/<int:classroom_id>/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/download/', views.download_teacher_quiz_report_pdf, name='download_teacher_quiz_report_pdf'),
    path('quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quiz/<int:quiz_id>/manage/', views.manage_quiz, name='manage_quiz'),
    path('get-questions/', views.get_questions, name='get_questions'),
    path('quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('unenroll/<int:classroom_id>/', unenroll_student, name='unenroll_student'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('save_question/', views.save_question, name='save_question'),
    path('add_existing_questions/', add_existing_questions, name='add_existing_questions'),
    path('accounts/', include('allauth.urls')),
    path('set-role/', views.set_role_password, name='set_role_password'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)