from django import template
from urllib.parse import urlparse, urlunparse
from django.http import QueryDict

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


@register.simple_tag
def file_url(obj):
    url_path = None
    try:
        url_path = obj.url
    except:
        pass
    return url_path
