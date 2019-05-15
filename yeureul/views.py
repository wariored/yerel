import os

from django.conf import settings as conf_settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from ads.models import Category
from . import forms
from .models import UserInfo, UserKey, ContactMessage
from ads.models import AdUser, Ad
from . import statics_variables


def handler404(request, exception):
    return render(request, 'error404.html', locals())


# index of the site
def index(request):
    categories = Category.objects.filter(category_type='T')
    categories_t_1 = categories[:4]
    categories_t_2 = categories[4:8]
    ads_count = Ad.manager_object.can_be_shown_to_public().all().count()
    return render(request, 'yeureul/index.html', dict(categories_t_1=categories_t_1,
                                                      categories_t_2=categories_t_2, ads_count=ads_count))


# robots and humans files
def home_files(request, filename):
    return render(request, filename, content_type="text/plain")


def cert_file(request):
    return render(request, "99797D4ABECAC61A30AB474DEC201FE2.txt", content_type="text/plain")


def login_view(request):
    """Login a user"""
    # no need to login if user is already authenticated
    if request.user.is_authenticated:
        return redirect('index')

    # redirection link
    redirect_to = request.GET.get('next', '/')
    reset_password = None
    if 'reset_password' in request.session:
        reset_password = request.session['reset_password']
        del request.session['reset_password']

    if request.method == 'POST':
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            email_username = form.data['email_username']
            email_username = email_username.lower()
            password = form.data['password']
            try:
                user = User.objects.get(email=email_username)
            except User.DoesNotExist:
                user = authenticate(request, username=email_username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not form.data.get('remember_me'):
                        request.session.set_expiry(0)
                    return redirect(redirect_to)
            else:
                return render(request, 'registration/login.html', {'form': form, 'login_error': True,
                                                                   'redirect_to': redirect_to,
                                                                   'reset_password': reset_password})
    else:
        form = forms.LoginForm()
    return render(request, 'registration/login.html', {'form': form, 'redirect_to': redirect_to,
                                                       'reset_password': reset_password})


def signup_view(request):
    """View for user signing up"""

    # if user has already signed in, redirect to the index view
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
    """Sign up form verification"""

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

        username = username.lower()
        username_exist = User.objects.filter(username=username).exists()
        email_exist = User.objects.filter(email=email).exists()

        if not (username_exist or email_exist):
            # create new user log it in
            User.objects.create_user(username, email, password_1)
            user = authenticate(request, username=username, password=password_1)
            login(request, user)

            # generate a token with the user as key, key_type="A" is for account Activation
            uid, token = uid_token_generator(user, key_type="A")
            url = conf_settings.BASE_URL + "account/validate/%s/%s" % (uid, token)

            # add user in UserInfo table
            UserInfo.objects.create(user=user, creation_date=timezone.now(), activated_account=False)

            # send email activation to the new user
            html_message = render_to_string('mails/account_activation.html', {'user': request.user, 'link': url})
            plain_message = strip_tags(html_message)
            email = EmailMessage('Yerel Email activation', plain_message, to=[user.email])
            email.send()

            return redirect('settings')
        else:
            # if we are here, it's because user does exist
            # generate an error and keep the values typed by the user
            # values are caught up in signup view
            request.session['signup_error'] = True
            request.session['dict_signup_values'] = dict_signup_values

            return redirect('signup')


def account_validation(request, uidb64=None, token=None):
    user_key = get_object_or_404(UserKey, key_type="A", token=token)
    check_token = uid_token_decoder(uidb64, token, key_type="A")
    if check_token:
        user_key.user.info.activated_account = True
        user_key.user.info.save()
        login(request, user_key.user)
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
    email = EmailMessage('Yerel Email activation', plain_message, to=[request.user.email])
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
            email = EmailMessage('Yerel mot de passe oublié ', plain_message, to=[user.email])
            email.send()
            return render(request, 'registration/before_password_reset.html', {'success': True})
    return render(request, 'registration/before_password_reset.html')


def account_reset_password(request, uidb64=None, token=None):
    user_key = get_object_or_404(UserKey, key_type="P", token=token)
    user = User.objects.get(pk=user_key.user.id)
    check_token = uid_token_decoder(uidb64=uidb64, token=token, key_type="P")
    if check_token:
        request.session['token'] = True
        request.session['user_id'] = user.id
        return redirect('password_reset')
    request.session['reset_password'] = False
    return redirect('login')


def password_reset(request):
    if request.session.get('token') or request.session.get('reset_password'):
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
    if 'activation' in request.session:
        activation = request.session['activation']
        del request.session['activation']
        return render(request, 'registration/account/settings.html', {'activation': activation})

    ad_user = AdUser.objects.filter(email=request.user.email).first()
    has_reached_ads_limit = ''
    if ad_user:
        if ad_user.has_reached_ads_limit(request):
            has_reached_ads_limit = 'ok'

    return render(request, 'registration/account/settings.html', {'update_profile_success': update_profile_success,
                                                                  'update_profile_error': update_profile_error,
                                                                  'has_reached_ads_limit': has_reached_ads_limit})


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
            if avatar.size < int(statics_variables.MAX_SIZE):
                try:
                    path = user_info.avatar.path
                    _delete_file(path)
                except ValueError:
                    pass
                user_info.avatar = avatar
            else:
                request.session['update_profile_error'] = 'avatar'
        if not request.session.get('update_profile_error'):
            user_info.save()
            user.save()
            try:
                user_ads = user.adUser
            except AdUser.DoesNotExist:
                pass
            else:
                user_ads.given_name = user.first_name + " " + user.last_name
                user_ads.save()
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


def faq(request):
    return render(request, 'yeureul/faq.html')


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


def uid_token_decoder(uidb64, token, key_type):
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
            return default_token_generator.check_token(user, token)
        except (User.DoesNotExist, UserKey.DoesNotExist):
            pass
    return False


def _delete_file(path):
    """ Deletes file from filesystem. """
    os.remove(path)
