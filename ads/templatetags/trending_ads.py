from django import template
from ads.models import Ad, Category, AdFeatured
from django.utils import timezone

register = template.Library()


@register.simple_tag
def trending_ads_list():
    two_weeks_before = timezone.now() - timezone.timedelta(days=14)
    ads = Ad.objects.filter(creation_date__range=(two_weeks_before, timezone.now()), is_deleted=False,
                            is_active=True).order_by('-views_number')[:8]
    return ads
