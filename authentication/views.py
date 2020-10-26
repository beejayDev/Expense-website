from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User

# Create your views here.
class registrationView(View):
    def get(self, request):
        return render(request, 'auth/register.html')


class usernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_errors': 'Username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_errors': 'Sorry username is in use! Please choose another one'}, status=400})
        return JsonResponse({'username-valid': True})



