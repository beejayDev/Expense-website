from .views import RegistrationView, verifyEmailView, LoginView, usernameValidationView, emailValidationView, LogoutView, RequestPasswordView, CompletePasswordResetView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
        path('register', RegistrationView.as_view(), name='register'),
        path('login', LoginView.as_view(), name='login'),
        path('logout', LogoutView.as_view(), name='logout'),
        path('validate-username',csrf_exempt(
            usernameValidationView.as_view()),
            name='validate-username'),
        path('validate-email', csrf_exempt(
            emailValidationView.as_view()), name='validate-email'),
        path('activate/<uidb64>/<token>', verifyEmailView.as_view(), name='activate'),
        path('request-reset-link', RequestPasswordView.as_view(), name='request-password'), 
        path('set-new-password/<uidb64>/<token>', CompletePasswordResetView.as_view(), name='reset-user-password'),
]
