from django.db import models
from django.contrib.auth.models import User

def info_file_name(instance, filename):
    return '/'.join(['info', instance.user.username, filename])

class UserInfo(models.Model):
	"""
	Other User informations
	"""
	user = models.OneToOneField(User, related_name='info', on_delete=models.CASCADE)
	phone_number= models.IntegerField(null=True, blank=True)
	address = models.CharField(max_length=200, null=True, blank=True)
	avatar = models.FileField(upload_to='avatar/', null=True, blank=True)
	activated_account = models.BooleanField(default=False)
	creation_date = models.DateTimeField('date created')
	updated_date = models.DateTimeField('date updated', auto_now_add=True)
	def __str__(self):
		return self.user.username