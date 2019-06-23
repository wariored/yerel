from django.db import models
from django.contrib.auth.models import User
import uuid
import os
from django.core.validators import URLValidator, MinLengthValidator, MaxLengthValidator


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('showrooms_avatar/', filename)


class Showroom(models.Model):
    name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    website = models.SlugField(validators=[URLValidator()], unique=True, null=True, blank=True)
    description = models.TextField(max_length=2000, null=True, blank=True)
    slogan = models.CharField(max_length=100, validators=[MinLengthValidator(3)], null=True, blank=True)
    phone_number_1 = models.PositiveIntegerField(null=True)
    phone_number_2 = models.PositiveIntegerField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    avatar = models.FileField(upload_to=get_file_path, null=True, blank=True)
    is_sponsored = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='showrooms', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
