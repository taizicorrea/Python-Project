from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path == reverse('login') and request.session.get('has_logged_in'):
                return redirect('landing')
        else:
            if request.path not in [reverse('login'), reverse('signup')]:
                return redirect('login')

        response = self.get_response(request)
        return response
