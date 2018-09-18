from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Category(models.Model):
	"""
	To store every adverstisement's category
	"""
	name = models.CharField(max_length=30, null=False)
	creation_date = models.DateTimeField('date created', auto_now_add=True)
	icon = models.CharField(max_length=250, null=True, blank=True)
	sup_category = models.ForeignKey('self', related_name='subcategory', null=True, blank=True, on_delete=models.PROTECT)
	#owner = models.ForeignKey('auth.User', related_name='categories', on_delete=models.PROTECT)
	def __str__(self):
		return self.name

class AdUser(models.Model):
	"""
	User who add an Ad, might be not authenticated
	"""
	given_name = models.CharField(max_length=50)
	phone_number= models.IntegerField(blank=True)
	email= models.EmailField(blank=True)
	user = models.ForeignKey(User, related_name='ads', null=True, blank=True, on_delete=models.CASCADE)
	creation_date = models.DateTimeField('date created', auto_now_add=True)
	def __str__(self):
		return self.phone_number + ' ' + self.given_name

class Location(models.Model):
	name = models.CharField(max_length=30)
	def __str__(self):
		return self.name

AD_CONDITION = (
    ('N', 'New'),
    ('U', 'Used'),
)
class Ad(models.Model):
	"""
	Where to store an Ad
	"""
	title = models.CharField(max_length=50)
	price = models.FloatField(max_length=30, validators=[MinValueValidator(500)])
	condition = models.CharField(max_length=1, choices=AD_CONDITION, blank=True)
	description = models.TextField(max_length=1000)
	subcategory = models.ForeignKey(Category, related_name='subcateg_ads', on_delete=models.PROTECT)
	location = models.ForeignKey(Location, related_name='loc_ads', on_delete=models.PROTECT)
	ad_user = models.ForeignKey(AdUser, related_name='ads', on_delete=models.CASCADE)
	creation_date = models.DateTimeField('date created')
	update_date = models.DateTimeField('date updated', auto_now_add=True)
	#owner = models.ForeignKey('auth.User', related_name='subcategories', on_delete=models.PROTECT)
	def __str__(self):
		return self.title

class AdFile(models.Model):
	"file related to an Ad"
	ad = models.ForeignKey(Ad, related_name='files', on_delete=models.CASCADE)
	media = models.FileField(upload_to='ads_files/')
	def __str__(self):
		return self.media