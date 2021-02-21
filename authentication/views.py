from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse 
from .utils import token_generator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading

#Create your views here.
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email 
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)
        
class registrationView(View):
    def get(self, request):
        return render(request, 'auth/register.html')


class usernameValidationView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_errors': 'Username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_errors': 'Sorry username is in use! Please choose another one'}, status=409)
        return JsonResponse({'username-valid': True})

class emailValidationView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_errors': 'Email should be a valid email!'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_errors': 'Sorry email is in use! Please choose another one'}, status=409)
        return JsonResponse({'email_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'auth/register.html')


    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        context = {
                'fieldValue': request.POST
                }

        if not (username and email and password):
            messages.error(request, "Please fill all fields")
            return render(request, 'auth/register.html', context)

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password is too short')
                    return render(request, 'auth/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

            #Steps in sending emails 
                #encoding uidb
                #Getting domain we're on
                current_site = get_current_site(request)

                #Composing the email_body
                email_body = {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': token_generator.make_token(user),
                        }

                #relative url to verification
                link = reverse('activate', kwargs = {
                    'uidb64': email_body['uid'],
                    'token': email_body['token']
                    })

                absurl = 'http://'+current_site.domain+link

                #Composing Email
                email_subject = 'Activate your email'
                email = EmailMessage(
                        email_subject,
                        f'Hi {user.username} Please use this link below to verify your account\n{absurl}',
                        'noreply@support.com',
                        [email],
                        )
                EmailThread(email).start()

                messages.success(request, 'Account created succesfully')
                return redirect('login')

        return render(request, 'auth/register.html', context)

#path to view
class verifyEmailView(View):
    def get(self, request, uidb64, token):
        try: 
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account successfully activated')
            return redirect('login')

        except Exception as ex:
            messages.error(request, 'Something went wrong')
            return redirect('login')


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'auth/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back {request.user.username} you are now logged in')
                    return redirect ('index')

                messages.error(request, 'Account not activated please check your email')
                return render(request, 'auth/login.html')

            messages.error(request, 'Invalid credentials! try again')
            return render(request, 'auth/login.html')

        messages.error(request, 'please fill all fields')
        return render(request, 'auth/login.html')


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'You\'ve successfully logged out')
        return redirect('login')


class RequestPasswordView(View):
    def get(self, request):
        return render(request, 'auth/reset-password.html')

    def post(self, request):
        email = request.POST['email']

        context = {
                'value': request.POST
                }

        if not validate_email(email):
            messages.error(request, 'Please enter a valid email')
            return render(request, 'auth/reset-password.html', context)

        #encoding uidb
        #Getting domain we're on
        current_site = get_current_site(request)

        user = User.objects.filter(email=email)

        if user.exists():
            #Composing the email_body
            email_content = {
                    'user': user[0],
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                    'token':PasswordResetTokenGenerator().make_token(user[0]),
                }

            #relative url to verification
            link = reverse('reset-user-password', kwargs = {
                'uidb64': email_content['uid'],
                'token': email_content['token']
                })
            reset_url = 'http://'+current_site.domain+link

            #Composing Email
            email_subject = 'Password reset instructions'
            email = EmailMessage(
                    email_subject,
                    f'Hi there Please use this link below to reset your password \n{reset_url}',
                    'noreply@support.com',
                    [email],
                    )
            email.send(fail_silently=False)
            EmailThread(email).start()

        messages.success(request, 'we\'ve sent you an email to reset your password')
        return render(request, 'auth/reset-password.html')

class CompletePasswordResetView(View):
    def get(self, request, uidb64, token):
        context = {
                'uidb64': uidb64,
                'token': token
                }
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link invalid! Please request a new one')
                return redirect('request-password')

        except Exception as identifier:
            pass

        return render(request, 'auth/set_new_password.html', context)

    def post(self, request, uidb64, token):
        context = {
                'uidb64': uidb64,
                'token': token
                }
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Password do not match')
            return render(request, 'auth/set_new_password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'auth/set_new_password.html', context)

        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset succesfully')
            return redirect('login')

        except Exception as identifier:
            messages.info(request, 'Something went wrong! try again')
            return render(request, 'auth/set_new_password.html', context)
        #return render(request, 'auth/set_new_password.html', context)
