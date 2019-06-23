from django import template
from ads.models import Ad, Category, Location
from django.db.models import Count

register = template.Library()


@register.filter(name="ads_number_category_showroom")
def ads_number_category_showroom(user_id, id_category):
    subcategories = []
    try:
        category = Category.objects.get(id=id_category, category_type='T')
    except Category.DoesNotExist:
        pass
    else:
        subcategories = category.subcategories.all()
    ads_count = 0
    for subcategory in subcategories:
        # add ads' number of a subcategory to the count
        ads_count += Ad.manager_object.can_be_shown_to_public().filter(subcategory=subcategory,
                                                                       ad_user__user__id=user_id).count()
    return ads_count
