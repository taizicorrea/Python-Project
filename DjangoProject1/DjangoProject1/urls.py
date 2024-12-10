# DjangoProject1/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Quiz_App.urls')),  # Include the Quiz_App URLs here
]
