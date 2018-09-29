from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import uuid
import os


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatar/', filename)


def one_day_hence():
    return timezone.now() + timezone.timedelta(days=1)


class UserInfo(models.Model):
    """
    Other User informations
    """
    user = models.OneToOneField(User, related_name='info', on_delete=models.CASCADE)  # 1 to 1 link with Django User
    phone_number = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    avatar = models.FileField(upload_to=get_file_path, null=True, blank=True)
    activated_account = models.BooleanField(default=False)
    creation_date = models.DateTimeField('date created')
    updated_date = models.DateTimeField('date updated', auto_now_add=True)

    def __str__(self):
        return self.user.username


KEY_TYPE = (
    ('P', 'PASSWORD'),
    ('A', 'ACTIVATION'),
)


class UserKey(models.Model):
    """
    Activation key for users
    """
    user = models.ForeignKey(User, related_name='keys', on_delete=models.CASCADE)  # 1 to many link with Django User
    key_type = models.CharField(max_length=1, choices=KEY_TYPE)
    token = models.CharField(max_length=100)
    key_expires = models.DateTimeField(default=one_day_hence)

    def __str__(self):
        return self.user.username + '_' + self.key_type


class ContactMessage(models.Model):
    """
    Message from site users
    """
    user = models.ForeignKey(User, related_name='contact_messages', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    message = models.TextField(max_length=2000)
