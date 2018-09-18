from django.db import models
from django.contrib.auth.models import User

import uuid
import os

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatar/', filename)


class UserInfo(models.Model):
	"""
	Other User informations
	"""
	user = models.OneToOneField(User, related_name='info', on_delete=models.CASCADE)
	phone_number= models.IntegerField(null=True, blank=True)
	address = models.CharField(max_length=200, null=True, blank=True)
	avatar = models.FileField(upload_to=get_file_path, null=True, blank=True)
	activated_account = models.BooleanField(default=False)
	creation_date = models.DateTimeField('date created')
	updated_date = models.DateTimeField('date updated', auto_now_add=True)
	def __str__(self):
		return self.user.username
		