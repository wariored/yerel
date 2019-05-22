from django import template
from ads.models import Ad, Category, AdFeatured
from django.utils import timezone

register = template.Library()


@register.simple_tag
def trending_ads_list():
    ads = Ad.manager_object.can_be_shown_to_public().filter().order_by('-creation_date')[:10]
    return ads
