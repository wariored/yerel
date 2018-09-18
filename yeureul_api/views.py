from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings as conf_settings
from django.db import transaction
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os

from .models import UserInfo

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes




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
        return redirect('login')
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

@transaction.atomic
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
            User.objects.create_user(username.lower(), email, password_1)
            user = authenticate(request, username=username, password=password_1)
            login(request, user)
            uid, token = uid_token_generator(user)
            url = conf_settings.BASE_URL + "account/validate/%s/%s" % (uid, token)
            html_message = render_to_string('mails/account_activation.html', {'user': request.user, 'link': url})
            plain_message = strip_tags(html_message)
            email = EmailMessage('Yeureul.org Email activation', plain_message, to=[user.email])
            email.send()
            UserInfo.objects.create(user=user, creation_date=timezone.now(), activated_account=False)
            return redirect('settings')
        else:
            request.session['signup_error'] = True
            request.session['dict_signup_values'] = dict_signup_values
            return redirect('signup')

def account_validation(request, uidb64=None, token=None):
    if uid_token_decoder(uidb64, token):
        user_info = UserInfo.objects.get(user=request.user)
        if user_info.activated_account == False:
            user_info.activated_account = True
            user_info.save()
            request.session['activation_success'] = True
        return redirect('settings')

    return HttpResponse("Une erreur est survenue")
    

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
    update_profile_error = request.session.get('update_profile_error')
    update_profile_success = request.session.get('update_profile_success')
    if update_profile_error:
        del request.session['update_profile_error']
    elif update_profile_success:
        del request.session['update_profile_success']
    if request.session.get('activation_success'):
        activation_success = request.session['activation_success']
        del request.session['activation_success']
        return render(request, 'registration/account/settings.html', {'activation_success': activation_success})

    return render(request, 'registration/account/settings.html', {'update_profile_success': update_profile_success,
        'update_profile_error': update_profile_error})

@transaction.atomic
def update_profile(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name', None)
        last_name = request.POST.get('last_name', None)
        address = request.POST.get('address', None)
        phone_number = request.POST.get('phone_number', None)
        avatar = request.FILES.get('avatar', None)
        old_password = request.POST.get('old_password', None)
        password_1 = request.POST.get('password_1', None)
        password_2 = request.POST.get('password_2', None)
        print(avatar)

        user = User.objects.get(username__exact=request.user.username)
        user_info = UserInfo.objects.get(user=user)
        if old_password:
            if request.user.check_password(old_password):
                if password_1:
                    if len(password_1) >= 5 and password_1 == password_2:
                        user.set_password(password_1)
                        login(request, user)
                    else:
                        request.session['update_profile_error'] = 'password'
                else:
                    request.session['update_profile_error'] = 'password'
            else:
                request.session['update_profile_error'] = 'old_password'
        if not first_name or not last_name:
            request.session['update_profile_error'] = 'first_last_name'
        else:
            user.first_name = first_name
            user.last_name = last_name
        try:
            int(phone_number)
        except:
            if not request.session.get('update_profile_error'):
                request.session['update_profile_error'] = 'phone_number'
        else:
            user_info.phone_number = phone_number
        user_info.address = address
        
        if avatar:
            if avatar.size < int(conf_settings.MAX_UPLOAD_SIZE):
                path = user_info.avatar.path
                _delete_file(path)
                user_info.avatar = avatar
            else:
                request.session['update_profile_error'] = 'avatar'
        if not request.session.get('update_profile_error'):
            user_info.save()
            user.save()
            request.session['update_profile_success'] = True


    return redirect('settings')
def contact(request):
    return render(request, 'yeureul_api/contact_us.html')


def uid_token_generator(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
    token = default_token_generator.make_token(user)
    return uid, token

def uid_token_decoder(uidb64, token):
    if uidb64 is not None and token is not None:
        from django.utils.http import urlsafe_base64_decode
        uid = force_text(urlsafe_base64_decode(uidb64).decode())
        try:
            from django.contrib.auth import get_user_model
            from django.contrib.auth.tokens import default_token_generator
            user_model = get_user_model()
            user = user_model.objects.get(pk=uid)
            return default_token_generator.check_token(user, token)
        except:
            pass

    return False


def _delete_file(path):
    """ Deletes file from filesystem. """
    os.remove(path)


