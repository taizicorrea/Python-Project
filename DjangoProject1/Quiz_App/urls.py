# Quiz_App/urls.py
from django.urls import path
from .views import signup_view, login_view, home_view, landing_page, logout_view, profile_view, join_class, create_class, account_management


urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('landing/', landing_page, name='landing'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('join-class/', join_class, name='join_class'),
    path('create-class/', create_class, name='create_class'),  # Add the new route
    path('account_management/', account_management, name='account_management'),
]
