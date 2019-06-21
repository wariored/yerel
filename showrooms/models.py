from django.db import models
from django.contrib.auth.models import User
import uuid, os


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('showrooms_avatar/', filename)


class Showroom(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    website = models.SlugField(unique=True)
    description = models.TextField(max_length=2000)
    phone_number_1 = models.IntegerField(null=True, blank=True)
    phone_number_2 = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    avatar = models.FileField(upload_to=get_file_path, null=True, blank=True)
    user = models.ForeignKey(User, related_name='showrooms', on_delete=models.CASCADE, blank=True, null=True)
