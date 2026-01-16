from django import template

register = template.Library()


@register.filter
def startswith(value, arg):
    """
    Custom filter to check if a string starts with a given prefix.
    Usage: {% if request.path|startswith:'/patients/' %}
    """
    return str(value).startswith(str(arg))
