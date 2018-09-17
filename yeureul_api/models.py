from django.db import models
from django.contrib.auth.models import User

def info_file_name(instance, filename):
    return '/'.join(['info', instance.user.username, filename])

class UserInfo(models.Model):
	"""
	Other User informations
	"""
	user = models.ForeignKey(User, related_name='user_info', on_delete=models.CASCADE)
	phone_number= models.IntegerField()
	address = models.CharField(max_length=200, null=True)
	avatar = models.FileField(upload_to='avatar/')
	creation_date = models.DateTimeField('date created')
	updated_date = models.DateTimeField('date updated', auto_now_add=True)