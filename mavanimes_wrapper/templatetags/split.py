from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split(string: str, sep: str | None=None) -> list:
    """Return a list of the substrings in the string, using sep as the separator string."""
    return string.split(sep)
