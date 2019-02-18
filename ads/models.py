from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from simple_history.models import HistoricalRecords
import uuid
import os
from pricing.models import Account
from yeureul import statics_variables


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('ads_file/', filename)


# if there is another category to add, we'll add it here
CATEGORY_TYPE = (
    ('T', 'TOP'),
    ('B', 'BOTTOM'),
)


class Category(models.Model):
    """
    To store every adverstisement's category
    """
    name = models.CharField(max_length=30, null=False)
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    icon = models.CharField(max_length=70, null=True, blank=True)
    widget = models.CharField(max_length=20, null=True, blank=True)
    category_type = models.CharField(max_length=10, null=True, blank=True, default='T', choices=CATEGORY_TYPE)
    sup_category = models.ForeignKey('self', related_name='subcategories', null=True, blank=True,
                                     on_delete=models.PROTECT)
    history = HistoricalRecords()

    # owner = models.ForeignKey('registration.User', related_name='categories', on_delete=models.PROTECT)

    def __str__(self):
        return self.name + ' _' + self.category_type


class AdUser(models.Model):
    """
    User who add an Ad, might be not authenticated
    """
    given_name = models.CharField(max_length=50)
    phone_number = models.IntegerField(null=True, blank=True)
    email = models.EmailField(blank=True)
    user = models.ForeignKey(User, related_name='ads', null=True, blank=True, on_delete=models.CASCADE)
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.email

    def has_reached_ads_limit(self, request):
        today = timezone.datetime.today()
        ads_number = Ad.objects.filter(ad_user__email=self.email, creation_date__month=today.month,
                                       creation_date__year=today.year).count()
        print(ads_number)

        if request.user.is_authenticated:
            user = request.user
            try:
                ads_in_the_month = Ad.objects.filter(ad_user__email=self.email, is_active=True,
                                                     creation_date__range=(user.account.active_date,
                                                                           user.account.end_date))
            except Account.DoesNotExist:
                if ads_number == 5:
                    return True
            else:
                ads_in_the_month_number = ads_in_the_month.count()
                if user.account.is_active():
                    if (
                            user.account.type == 'N' and
                            ads_in_the_month_number == statics_variables.MAX_NORMAL) or (
                            user.account.type == 'A' and
                            ads_in_the_month_number == statics_variables.MAx_ADVANCED):
                        return True
                else:
                    return True
        else:
            if ads_number == statics_variables.MAX_NONE:
                return True

        return False


class Location(models.Model):
    name = models.CharField(max_length=30)
    history = HistoricalRecords()

    def __str__(self):
        return '%s' % self.name


AD_CONDITION = (
    ('N', 'Nouvelle'),
    ('U', 'Utilisée'),
)


class Ad(models.Model):
    """
    Where to store an Ad
    """
    title = models.CharField(max_length=50)
    price = models.FloatField(max_length=30, validators=[MinValueValidator(500)])
    condition = models.CharField(max_length=1, choices=AD_CONDITION, blank=True)
    description = models.TextField(max_length=2000)
    random_url = models.UUIDField(default=uuid.uuid4)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    subcategory = models.ForeignKey(Category, related_name='subcateg_ads', on_delete=models.PROTECT)
    location = models.ForeignKey(Location, related_name='loc_ads', on_delete=models.PROTECT)
    ad_user = models.ForeignKey(AdUser, related_name='ads', on_delete=models.CASCADE)
    creation_date = models.DateTimeField('da    te created')
    update_date = models.DateTimeField('date updated', auto_now_add=True)
    views_number = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name='post_likes')
    history = HistoricalRecords()

    def __str__(self):
        return self.title


class AdFile(models.Model):
    """Images related to an Ad"""
    ad = models.ForeignKey(Ad, related_name='img', on_delete=models.CASCADE)
    media = models.ImageField(upload_to=get_file_path)
    history = HistoricalRecords()

    def __str__(self):
        return self.ad.title + '_' + str(self.id)
