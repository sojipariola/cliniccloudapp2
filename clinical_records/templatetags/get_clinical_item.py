
from django import template

register = template.Library()
# Change the tag name if needed, e.g.:

@register.filter(name='get_clinical_item')
def get_clinical_item(dictionary, key):
    return dictionary.get(key)