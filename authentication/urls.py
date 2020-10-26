from .views import registrationView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
        path('register', registrationView.as_view(), name='register'),
        path('validate-username',csrf_exempt(
            usernameValidationView.as_view()),
            name='validate-email'),
        ]
