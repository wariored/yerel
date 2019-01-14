from django import template
from ads.models import Ad, Category

register = template.Library()


@register.inclusion_tag('header_footer/ads_categories.html')
def count_ads_by_categories():
    dict_adsnumber_categories = dict()
    list_of_sup_categories = list()
    for category in Category.objects.filter(category_type='B'):
        if category.sup_category not in list_of_sup_categories:
            list_of_sup_categories.append(category.sup_category)
            dict_adsnumber_categories[category.sup_category.name] = Ad.objects.filter(
                subcategory=Category.objects.get(id=category.id)).count()
        else:
            dict_adsnumber_categories[category.sup_category.name] += Ad.objects.filter(
                subcategory=Category.objects.get(id=category.id)).count()
    return {'count_ads_categories': dict_adsnumber_categories}
