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

from .models import UserInfo, UserKey, ContactMessage
from ads.models import Category, AdUser, Ad, AdFile, Location

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


# index of the site
def index(request):
    categories_t_1 = Category.objects.filter(category_type='T',
                                             name__in=['Restaurant', 'Immobilier', 'Shopping', 'Voitures'])
    categories_t_2 = Category.objects.filter(category_type='T', name__in=['Emploi', 'Hotels', 'Services', 'Animaux'])
    return render(request, 'yeureul/index.html',
                  {
            'categories_t_1': categories_t_1,
            'categories_t_2': categories_t_2,
        }
                  )


# robots and humans files
def home_files(request, filename):
    return render(request, filename, content_type="text/plain")


def login_view(request):
    redirect_to = request.GET.get('next', '/')
    close_account = request.session.get('close_account', None)
    reset_password = request.session.get('reset_password', None)
    if request.user.is_authenticated:
        return redirect('index')
    if close_account is not None:
        del request.session['close_account']
    if reset_password is not None:
        del request.session['reset_password']
    if request.session.get('login_error') is not None:
        del request.session['login_error']
        return render(request, 'registration/login.html',
                      dict(login_error=True, redirect_to=redirect_to, close_account=close_account)
                      )
    return render(request, 'registration/login.html',
                  dict(redirect_to=redirect_to, close_account=close_account, reset_password=reset_password)
                  )


def login_verification(request):
    """
    Login a user
    """
    redirect_to = request.GET.get('next', '/')
    if request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        email_or_username = request.POST['email_or_username']
        email_or_username = email_or_username.lower()
        password = request.POST['password']
        user = authenticate(request, username=email_or_username, password=password)
        if user is None:
            try:
                user = User.objects.get(email__iexact=email_or_username)
            except:
                pass
            else:
                if not user.check_password(password):
                    user = None
        if user is not None:
            if user.is_active:
                login(request, user)
                if not request.POST.get('remember_me', None):
                    request.session.set_expiry(0)
                return redirect(redirect_to)
            else:
                request.session['close_account'] = True
                return redirect('/login/?next=%s' % redirect_to)
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
            uid, token = uid_token_generator(user, key_type="A")
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
    if uid_token_decoder(uidb64, token, request.user, key_type="A"):
        user_info = UserInfo.objects.get(user=request.user)
        if user_info.activated_account == False:
            user_info.activated_account = True
            user_info.save()
            request.session['activation'] = True
            return redirect('settings')
    request.session['activation'] = 'key_expired'
    return redirect('settings')


@login_required
def regenerate_activation_link(request):
    if request.user.info.activated_account:
        return redirect('settings')
    uid, token = uid_token_generator(request.user, key_type="A")
    url = conf_settings.BASE_URL + "account/validate/%s/%s" % (uid, token)
    html_message = render_to_string('mails/account_activation.html', {'user': request.user, 'link': url})
    plain_message = strip_tags(html_message)
    email = EmailMessage('Yeureul.org Email activation', plain_message, to=[request.user.email])
    email.send()
    request.session['activation'] = 'regenerate_activation_link'
    return redirect('settings')


def before_password_reset(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'registration/before_password_reset.html', {'not_exist': True, 'email': email})
        else:
            uid, token = uid_token_generator(user, key_type="P")
            url = conf_settings.BASE_URL + "account/reset_password/%s/%s" % (uid, token)
            html_message = render_to_string('mails/password_reset.html', {'user': user.username, 'link': url})
            plain_message = strip_tags(html_message)
            email = EmailMessage('Yeureul.org mot de passe oublié ', plain_message, to=[user.email])
            email.send()
            return render(request, 'registration/before_password_reset.html', {'success': True})
    return render(request, 'registration/before_password_reset.html')


def account_reset_password(request, uidb64=None, token=None):
    user_key = get_object_or_404(UserKey, key_type="P", token=token)
    user = User.objects.get(pk=user_key.user.id)
    if uid_token_decoder(uidb64=uidb64, token=token, user=user, key_type="P"):
        request.session['token'] = True
        request.session['user_id'] = user.id
        return redirect('password_reset')
    request.session['reset_password'] = False
    return redirect('login')


def password_reset(request):
    if request.session.get('token') == True or request.session.get('reset_password'):
        if request.session.get('reset_password'):
            user_id = request.session['reset_password']
            error = True
            del request.session['reset_password']
        else:
            user_id = request.session['user_id']
            error = False
            del request.session['token']
            del request.session['user_id']
        return render(request, 'registration/password_reset.html', {'user_id': user_id, 'error': error})
    return redirect('index')


def password_reset_verification(request):
    if request.method == "POST":
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']
        user_id = request.POST['user_id']
        if password_1:
            if len(password_1) >= 5 and password_1 == password_2:
                user = get_object_or_404(User, id=user_id)
                user.set_password(password_1)
                user.save()
                request.session['reset_password'] = True
                return redirect('login')
            else:
                request.session['reset_password'] = user_id
        else:
            request.session['reset_password'] = user_id
        return redirect('password_reset')
    return redirect('login')


# to logout a user
@login_required
def logout_view(request):
    logout(request)
    request.session['lastConnectionDate'] = str(timezone.now())
    return redirect('index')


@login_required
def settings(request):
    update_profile_error = request.session.get('update_profile_error')
    update_profile_success = request.session.get('update_profile_success')
    if update_profile_error:
        del request.session['update_profile_error']
    elif update_profile_success:
        del request.session['update_profile_success']
    if request.session.get('activation'):
        activation = request.session['activation']
        del request.session['activation']
        return render(request, 'registration/account/settings.html', {'activation': activation})

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
    contact_error = request.session.get('contact', None)
    list_values = request.session.get('list_values', None)
    if contact_error:
        del request.session['contact']
    if list_values:
        del request.session['list_values']
    return render(request, 'yeureul/contact_us.html', {'contact': contact_error, 'list_values': list_values})


@transaction.atomic
def contact_verification(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            subject = request.POST['subject']
            message = request.POST['message']
            if not message:
                request.session['contact'] = 'message_error'
                return redirect('contact')
            ContactMessage.objects.create(user=request.user, subject=subject, message=message)
            request.session['contact'] = 'success'
        else:
            name = request.POST['name']
            email = request.POST['email']
            subject = request.POST['subject']
            message = request.POST['message']
            list_values = {'name': name, 'email': email, 'subject': subject, 'message': message}
            if not name or not message:
                request.session['contact'] = 'name_message_error'
                request.session['list_values'] = list_values
                return redirect('contact')
            else:
                try:
                    validate_email(email)
                except:
                    request.session['contact'] = 'email_error'
                    request.session['list_values'] = list_values
                    return redirect('contact')
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            request.session['contact'] = 'success'
    return redirect('contact')


@login_required
def close_account(request):
    return render(request, 'registration/account/close_account.html')


@login_required
def close_account_verification(request):
    if request.method == "POST":
        close = request.POST['close']
        if close == 'yes':
            user = User.objects.get(pk=request.user.id)
            user.is_active = False
            user.save()
            request.session['close_account'] = True
            return redirect('login')
    return redirect('settings')


def uid_token_generator(user, key_type):
    uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
    token = default_token_generator.make_token(user)
    key_to_update, key_created = UserKey.objects.get_or_create(user=user, key_type=key_type)
    if not key_created:  # do not forget to make a constraint for only 2 entries in UserKey
        key_to_update.key_expires = timezone.now() + timezone.timedelta(days=1)
        key_to_update.token = token
        key_to_update.save()
    else:
        key_to_update.token = token
        key_to_update.save()
    return uid, token


def uid_token_decoder(uidb64, token, user, key_type):
    if uidb64 is not None and token is not None:
        from django.utils.http import urlsafe_base64_decode
        uid = force_text(urlsafe_base64_decode(uidb64).decode())
        try:
            from django.contrib.auth import get_user_model
            from django.contrib.auth.tokens import default_token_generator
            user_model = get_user_model()
            user = user_model.objects.get(pk=uid)
            user_key = UserKey.objects.get(user=user, key_type=key_type, token=token)
            if user_key.key_expires < timezone.now():
                return False
            else:
                return default_token_generator.check_token(user, token)
        except:
            pass

    return False


def _delete_file(path):
    """ Deletes file from filesystem. """
    os.remove(path)
