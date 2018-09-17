from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone

# index of the site
def index(request):
    return render(request, 'yeureul_api/index.html')


# robots and humans files
def home_files(request, filename):
    return render(request, filename, content_type="text/plain")



def login_view(request):
    redirect_to = request.GET.get('next', '/')
    if request.user.is_authenticated:
        return redirect('index')
    if request.session.get('login_error'):
        del request.session['login_error']
        return render(request, 'registration/login.html', {"login_error": True, 'redirect_to': redirect_to})
    return render(request, 'registration/login.html', {'redirect_to': redirect_to})


def login_verification(request):
    """
    Login a user
    """
    redirect_to = request.GET.get('next', '/')
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    if request.method == "POST":
        email_or_username = request.POST['email_or_username']
        password = request.POST['password']
        user = authenticate(request, username=email_or_username, password=password)
        if user is None:
            user = authenticate(request, email=email_or_username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if not request.POST.get('remember_me', None):
                    request.session.set_expiry(0)
                return redirect(redirect_to)
            return HttpResponse("You are not allowed to log in")
        request.session['login_error'] = True
        return redirect('/login/?next=%s' % redirect_to)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.session.get('signup_error'):
        signup_error = request.session['signup_error']
        dict_signup_values = request.session['dict_signup_values']
        del request.session['signup_error']
        del request.session['dict_signup_values']
        return render(request, 'registration/signup.html', 
            {"signup_error": signup_error, 'dict_signup_values': dict_signup_values})
    return render(request, 'registration/signup.html')

def signup_verification(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']
        agreed_terms = request.POST.get('terms', None)
        dict_signup_values = {'username': username, 'email': email}
        try:
            validate_email(email)
        except:
            request.session['signup_error'] = 'email_error'
            request.session['dict_signup_values'] = dict_signup_values
            return redirect('signup')
        if password_1 != password_2 or len(password_1) < 5:
            request.session['signup_error'] = 'password_error'
            request.session['dict_signup_values'] = dict_signup_values
            return redirect('signup')
        elif agreed_terms is None:
            request.session['signup_error'] = 'terms_error'
            request.session['dict_signup_values'] = dict_signup_values
            return redirect('signup')
        if not (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):
            User.objects.create_user(username, email, password_1)
            user = authenticate(request, username=username, password=password_1)
            login(request, user)
            request.session['signup_success'] = True
            return redirect('settings')
        else:
            request.session['signup_error'] = True
            request.session['dict_signup_values'] = dict_signup_values
            return redirect('signup')

# to logout a user
@login_required
def logout_view(request):
    logout(request)
    request.session['lastConnectionDate'] = str(timezone.now())
    return redirect('index')


def password_reset(request):
    return render(request, 'registration/password_reset.html')


@login_required
def password_change(request):
    if request.method == "POST":
        oldpassword = request.POST['oldpassword']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if ((password1 != password2) or (password1 == "")):
            errorMessage = "New password sould not be empty and should be the same than the repeated password"
            return render(request, 'registration/password_change.html', {"errorMessage": errorMessage})
        if request.user.check_password(oldpassword):
            request.user.password = password1
            successMessage = "Your password has been successfully changed"
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(password1)
            u.save()
            login(request, u)
            return render(request, 'registration/password_change.html', {"successMessage": successMessage})
        else:
            errorMessage = "Your current password is not correct. Please, provide a correct one"
            return render(request, 'registration/password_change.html', {"errorMessage": errorMessage})
    return render(request, 'registration/password_change.html')

@login_required
def settings(request):
    return render(request, 'registration/account/settings.html')

def contact(request):
    return render(request, 'yeureul_api/contact_us.html')
