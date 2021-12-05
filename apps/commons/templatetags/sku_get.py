from django import template
from django.template.defaultfilters import stringfilter
import json

register = template.Library()

@register.filter
@stringfilter
def sku_get(sku_array, sku_number):
    """Return the string split by sep.

    Example usage: {{ sku_array|sku_get:sku_number }}
    """
    res = []
    for sku in json.loads(sku_array.replace("'", '"')):
        if sku['sku_number'] == sku_number:
           for attr in sku['attr_array']:
               res.append(attr['value'])
    return res