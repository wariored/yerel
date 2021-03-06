from django import template
from ads.models import Ad, Category, AdFeatured
from django.utils import timezone

register = template.Library()


def ads_featured_sorted(ad):
    try:
        ad.feature
    except AdFeatured.DoesNotExist:
        pass
    else:
        return ad.feature.start_date
    return ad.creation_date


@register.simple_tag
def featured(category_id):
    category = Category.objects.get(pk=category_id)
    subcategories = category.subcategories.all()
    list_ads = list()
    for subcategory in subcategories:
        # subcategory.subcateg_ads.filter(is_active=True, is_deleted=False).order_by('-feature__start_date')[:5]
        ads = Ad.manager_object.can_be_shown_to_public().filter(subcategory=subcategory).order_by('-feature__start_date')[:5]
        for ad in ads:
            list_ads.append(ad)
    list_ads.sort(key=ads_featured_sorted, reverse=True)

    return list_ads
