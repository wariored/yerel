from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
import os
from pricing.models import Account
from yeureul import statics_variables, utils_functions
from showrooms.models import Showroom


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
    To store every advertisement's category
    """
    name = models.CharField(max_length=30, null=False)
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    icon = models.CharField(max_length=70, null=True, blank=True)
    icon_ads = models.CharField(max_length=70, null=True, blank=True)
    widget = models.CharField(max_length=20, null=True, blank=True)
    category_type = models.CharField(
        max_length=20, null=True, blank=True, default='T', choices=CATEGORY_TYPE)
    sup_category = models.ForeignKey('self', related_name='subcategories', null=True, blank=True,
                                     on_delete=models.PROTECT)
    degree = models.IntegerField(default=0)

    # owner = models.ForeignKey('registration.User', related_name='categories', on_delete=models.PROTECT)

    def __str__(self):
        return self.name + ' _' + self.category_type


class AdUser(models.Model):
    """
    User who add an Ad, might be not authenticated that's why we have this class
    """
    given_name = models.CharField(max_length=50)
    phone_number = models.IntegerField(null=True, blank=True)
    email = models.EmailField(blank=True)
    user = models.OneToOneField(
        User, related_name='adUser', null=True, blank=True, on_delete=models.CASCADE)
    creation_date = models.DateTimeField('date created', auto_now_add=True)
    showroom = models.OneToOneField(Showroom, related_name='showroom_adUser', on_delete=models.SET_NULL, null=True,
                                    blank=True)

    def __str__(self):
        return self.email

    def has_reached_ads_limit(self, request):
        # today = timezone.datetime.today()
        # ads_number = Ad.objects.filter(ad_user__email=self.email, creation_date__month=today.month,
        #                                creation_date__year=today.year).count()
        #
        # if request.user.is_authenticated:
        #     user = request.user
        #     try:
        #         ads_in_the_month = Ad.objects.filter(ad_user__email=self.email, is_active=True,
        #                                              creation_date__range=(user.account.active_date,
        #                                                                    user.account.end_date))
        #     except Account.DoesNotExist:
        #         if ads_number == 5:
        #             return True
        #     else:
        #         ads_in_the_month_number = ads_in_the_month.count()
        #         if user.account.is_active():
        #             if (
        #                     user.account.type == 'N' and
        #                     ads_in_the_month_number == statics_variables.MAX_NORMAL) or (
        #                     user.account.type == 'A' and
        #                     ads_in_the_month_number == statics_variables.MAX_ADVANCED):
        #                 return True
        #         else:
        #             return True
        # else:
        #     if ads_number == statics_variables.MAX_NONE:
        #         return True
        #
        # return False
        return False


class Location(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return '%s' % self.name


AD_CONDITION = (
    ('N', 'Nouvelle'),
    ('U', 'Utilisée'),
)


class AdManager(models.Manager):
    # if a function in this class is changed, the corresponding function in Ad class should be changed too
    def can_be_shown_to_public(self):
        return super().get_queryset().filter(is_active=True, is_deleted=False, on_pause=False)

    def can_be_shown_to_owner(self):
        return super().get_queryset().filter(is_deleted=False)

    def can_be_edited(self):
        return super().get_queryset().filter(is_deleted=False, on_pause=False)


class Ad(models.Model):
    """
    Where to store an Ad
    """
    title = models.CharField(max_length=50)
    price = models.FloatField(max_length=30, default=0)
    condition = models.CharField(max_length=1, choices=AD_CONDITION, blank=True)
    description = models.TextField(max_length=2000)
    random_url = models.UUIDField(default=uuid.uuid4, editable=False)
    random_code = models.CharField(max_length=10, blank=True, editable=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    # an ad is on pause when it's reported many times
    on_pause = models.BooleanField(default=False)
    subcategory = models.ForeignKey(Category, related_name='subcateg_ads', on_delete=models.PROTECT)
    location = models.ForeignKey(Location, related_name='loc_ads', on_delete=models.PROTECT)
    ad_user = models.ForeignKey(AdUser, related_name='ads', on_delete=models.CASCADE)
    creation_date = models.DateTimeField('date created')
    update_date = models.DateTimeField('date updated', default=timezone.now)
    views_number = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name='post_likes')
    objects = models.Manager()
    manager_object = AdManager()

    def __str__(self):
        return self.title

    def is_featured(self):
        try:
            AdFeatured.objects.get(ad=self)
        except AdFeatured.DoesNotExist:
            return False
        else:
            return True

    def can_be_shown_to_public(self):
        return self.is_active and not self.is_deleted and not self.on_pause

    def can_be_shown_to_owner(self):
        return not self.is_deleted

    def can_be_edited(self):
        return not self.is_deleted and not self.on_pause


class AdFile(models.Model):
    """Images related to an Ad"""
    ad = models.ForeignKey(Ad, related_name='img', on_delete=models.CASCADE)
    media = models.ImageField(upload_to=get_file_path)

    def __str__(self):
        return self.ad.title + '_' + str(self.id)

    def save(self, *args, **kwargs):
        try:
            # call the compress function
            new_image = utils_functions.compress_image(self.media)
            # set self.image to new_image
        except ValueError:
            pass
        else:
            self.media = new_image
        # save
        super().save(*args, **kwargs)


def two_days_hence():
    return timezone.now() + timezone.timedelta(days=2)


class AdFeatured(models.Model):
    ad = models.OneToOneField(Ad, related_name='feature', on_delete=models.CASCADE)
    start_date = models.DateTimeField('start date', auto_now_add=True)
    end_date = models.DateTimeField('end date', default=two_days_hence)

    def is_active(self):
        if self.end_date > timezone.now():
            return True

        return False


class HistoricalFeatured(models.Model):
    """
    This is Historical record for the Model AdFeatured
    """
    ad_id = models.IntegerField(unique=True)
    date = models.DateTimeField('start date', default=timezone.now)


ALERT_TYPE = (
    ('D', 'DAY'),
    ('W', 'WEEK'),
    ('M', 'MONTH'),
)


class Alert(models.Model):
    user = models.ForeignKey(User, related_name='alerts', on_delete=models.CASCADE)
    email = models.EmailField()
    frequency = models.CharField(max_length=1, choices=ALERT_TYPE)
    category = models.ForeignKey(Category, related_name='categ_alerts', on_delete=models.CASCADE)

    def __str__(self):
        return self.email + "_" + str(self.frequency) + "_" + self.category.name


SIGNAL_TYPE = (
    ('AI', 'Annonce inappropriée'),
    ('AA', 'Annonce avec du contenu abusif'),
    ('AC', 'Autre choses')
)


class Signal(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='signals')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='my_signals', null=True)
    type = models.CharField(max_length=50, choices=SIGNAL_TYPE)

    def __str__(self):
        return self.ad.title + " => " + self.type
