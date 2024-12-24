from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, None)