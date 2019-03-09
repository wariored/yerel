from django import template
from django.utils.timesince import timesince
from django.utils import timezone
import datetime

register = template.Library()


@register.filter
def timesince_creation(creation_date):
    timedelta_creation = datetime.datetime.now(timezone.utc) - creation_date
    if timedelta_creation.days == 0 and timedelta_creation.seconds < 60:
        return "À l'instant"
    return 'Il y a ' + timesince(creation_date).split(",")[0]
