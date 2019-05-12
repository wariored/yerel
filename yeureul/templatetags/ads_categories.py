from django import template
from ads.models import Ad, Category, Location
from django.db.models import Count

register = template.Library()


@register.inclusion_tag('header_footer/ads_categories.html')
def count_ads_by_categories():
    #  dict of ads' number by name of category
    dict_ads_number_categories = dict()
    # get all categories
    categories = Category.objects.filter(category_type='T')
    for category in categories:
        # get all subcategories of the category
        subcategories = category.subcategories.all()
        # init the ads number to zero
        ads_count = 0
        for subcategory in subcategories:
            # add ads' number of a subcategory to the count
            ads_count += Ad.objects.filter(subcategory=subcategory, is_active=True, is_deleted=False).count()

        # key = category's name; value = number of active and non deleted ads
        dict_ads_number_categories[category.name] = ads_count

    # for category in Category.objects.filter(category_type='B'):
    #     if category.sup_category not in list_of_sup_categories:
    #         list_of_sup_categories.append(category.sup_category)
    #         dict_adsnumber_categories[category.sup_category.name] = Ad.objects.filter(
    #             subcategory=Category.objects.get(id=category.id)).count()
    #     else:
    #         dict_adsnumber_categories[category.sup_category.name] += Ad.objects.filter(
    #             subcategory=Category.objects.get(id=category.id)).count()
    return {'count_ads_categories': dict_ads_number_categories}


# get last published ads (active and not deleted)
@register.inclusion_tag('header_footer/ads_categories.html')
def last_ad(count=3):
    # the last ad
    last = list()
    try:
        last = Ad.objects.filter(is_active=True, is_deleted=False).order_by('-creation_date')[:count]
    except IndexError:
        pass
    return {'last_three_ads': last}


@register.filter(name="ads_number")
def ads_number(id_category):
    category = Category.objects.get(id=id_category, category_type='T')
    ads_count = 0
    for subcategory in category.subcategories.all():
        # add ads' number of a subcategory to the count
        ads_count += Ad.manager_object.can_be_shown_to_public().filter(subcategory=subcategory).count()
    return ads_count


@register.simple_tag
def categories_and_subcategories():
    categories_t = Category.objects.filter(category_type='T')
    return categories_t


@register.simple_tag
def locations():
    locations_all = Location.objects.all()
    return locations_all


@register.simple_tag
def popular_subcategories():
    populars = Category.objects.filter(category_type='B').annotate(count=Count('subcateg_ads')).order_by('-count')
    return populars[:5]


@register.filter
def likes_number(user_id):
    num = Ad.manager_object.can_be_shown_to_public().filter(likes__id=user_id).count()
    return num
