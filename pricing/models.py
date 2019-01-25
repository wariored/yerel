from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

PRICING_TYPE = (
    ('N', 'NORMAL'),
    ('A', 'ADVANCED'),
    ('P', 'PROFESSIONAL')
)


def one_month_hence():
    return timezone.now() + timezone.timedelta(days=31)


class Pricing(models.Model):
    type = models.CharField(max_length=1, choices=PRICING_TYPE)
    active_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=one_month_hence)
    user = models.OneToOneField(User, related_name='pricing', on_delete=models.PROTECT)

    def clean(self):
        pass

    def is_active(self):
        return self.end_date > timezone.now()


class PricingHistory(models.Model):
    pricing = models.ForeignKey(Pricing, related_name='histories', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    token = models.CharField(max_length=255)
    amount = models.IntegerField()

