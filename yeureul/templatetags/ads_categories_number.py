from django import template

register = template.Library()

from ads.models import Ad , Category 

# @register.tag()
# def count_ads_by_categories():
#     d = dict()
#     sup = list()
#     for category in Category.objects.filter(category_type='B'):
#         if category.sup_category not in sup:
#             sup.append(category.sup_category)
#             d[category.sup_category.name]=Ad.objects.filter(subcategory=Category.objects.get(name=category.name)).count()
#         else:
#             d[category.sup_category.name]+=Ad.objects.filter(subcategory=Category.objects.get(name=category.name)).count()
#     return d
# @register.simple_tag()
# def count_ads_by_categories():
#     d = dict()
#     sup = list()
#     for category in Category.objects.filter(category_type='B'):
#         if category.sup_category not in sup:
#             sup.append(category.sup_category)
#             d[category.sup_category.name]=Ad.objects.filter(subcategory=Category.objects.get(name=category.name)).count()
#         else:
#             d[category.sup_category.name]+=Ad.objects.filter(subcategory=Category.objects.get(name=category.name)).count()
#     return d.keys()
@register.inclusion_tag('header_footer/header.html')
def count_ads_by_categories1():
    d = dict()
    sup = list()
    for category in Category.objects.filter(category_type='B'):
        if category.sup_category not in sup:
            sup.append(category.sup_category)
            d[category.sup_category.name]=Ad.objects.filter(subcategory=Category.objects.get(name=category.name)).count()
        else:
            d[category.sup_category.name]+=Ad.objects.filter(subcategory=Category.objects.get(name=category.name)).count()
    return {'count_ads_by_categories':d}