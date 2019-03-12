from django import template

register = template.Library()


@register.filter
def is_in(var, obj):
    return var in obj.split(',')
