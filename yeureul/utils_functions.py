from difflib import SequenceMatcher
from django.utils import timezone
import os
import random
import string
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.apps import apps
from django.core.mail import EmailMessage
from django.utils.html import strip_tags


def similar(a, b):
    """ compute the similarity of two string """
    return SequenceMatcher(None, a, b).ratio()


def ads_are_similar(ads_1, ads_2):
    """ If strings ratio is more or equal than 0.5 then it's fine """
    if similar(ads_1, ads_2) >= 0.5:
        return True

    return False


def days_hence(days):
    return timezone.now() + timezone.timedelta(days=days)


def _delete_file(path):
    """ Deletes file from filesystem. """
    os.remove(path)


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def compress_image(image):
    im = Image.open(image)
    # create a BytesIO object
    im_io = BytesIO()
    # save image to BytesIO object
    im.save(im_io, 'JPEG', quality=20)
    # create a django-friendly Files object
    new_image = File(im_io, name=image.name)
    return new_image


def uid_token_generator(user, key_type):
    UserKey = apps.get_model('yeureul.UserKey')
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
    UserKey = apps.get_model('yeureul.UserKey')
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


def send_email(html_message, subject, to: list):
    plain_message = strip_tags(html_message)
    email = EmailMessage(subject, plain_message, to=to)
    email.send()
