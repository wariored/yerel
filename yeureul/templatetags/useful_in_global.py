from django import template
from urllib.parse import urlparse, urlunparse
from django.http import QueryDict
from ads.models import Ad

register = template.Library()


@register.filter
def is_in(var, obj):
    return var in obj.split(',')


@register.simple_tag
def replace_query_param(url, attr, val):
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    query_dict = QueryDict(query).copy()
    query_dict[attr] = val
    query = query_dict.urlencode()
    return urlunparse((scheme, netloc, path, params, query, fragment))


@register.simple_tag
def define_variable(val=None):
    return val


@register.filter
def count_ads_in_subcategory(subcategory_id):
    count = Ad.manager_object.can_be_shown_to_public().filter(subcategory__id=subcategory_id).count()
    return count

@register.filter
def count_ads_for_adUser(ad_user_id):
    count = Ad.manager_object.can_be_shown_to_owner().filter(ad_user__id=ad_user_id).count()
    return count
