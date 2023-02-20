from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def append(items: str, value=str) -> str:
    """Return a list of items different from value."""
    return ','.join(item for item in items.split(',') + [value] if item)
