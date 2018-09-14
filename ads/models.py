from django.db import models
from django.utils import timezone
import datetime

class Category(models.Model):
	"""
	To store every adverstisement's category
	"""
	name = models.CharField(max_length=30, null=False)
	creation_date = models.DateTimeField('date created', auto_now_add=True)
	icon = models.CharField(max_length=250, null=True)
	#owner = models.ForeignKey('auth.User', related_name='categories', on_delete=models.PROTECT)
	def __str__(self):
		return self.name

class Subcategory(models.Model):
	"""
	A subcategory have at least one subcategory that we store here
	"""
	category = models.ForeignKey(Category, related_name='categ_subcategs', on_delete=models.CASCADE)
	name = models.CharField(max_length=30, null=False)
	creation_date = models.DateTimeField('date created', auto_now_add=True)
	#owner = models.ForeignKey('auth.User', related_name='subcategories', on_delete=models.PROTECT)
	def __str__(self):
		return self.name