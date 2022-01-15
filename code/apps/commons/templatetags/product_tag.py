from django import template
register = template.Library()

@register.simple_tag
def product_tag(val=None):
  return (int(val) - 1) * 21