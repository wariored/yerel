from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

PRICING_TYPE = (
    ('N', 'NORMAL'),
    ('A', 'ADVANCED'),
    ('P', 'PROFESSIONAL')
)


def one_month_hence():
    return timezone.now() + timezone.timedelta(days=31)


class Account(models.Model):
    type = models.CharField(max_length=1, choices=PRICING_TYPE)
    active_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=one_month_hence)
    token = models.CharField(max_length=255)
    user = models.OneToOneField(User, related_name='account', on_delete=models.PROTECT)
    history = HistoricalRecords()

    def clean(self):
        pass

    def is_active(self):
        return self.end_date > timezone.now()
