# reservation/templatetags/url_tags.py
from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Remplace ou ajoute des paramètres GET dans l'URL
    Utilisé pour préserver les filtres lors de la pagination
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return urlencode(query)