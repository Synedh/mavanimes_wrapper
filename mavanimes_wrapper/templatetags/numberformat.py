from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def numberformat(numstring: str) -> float:
    """Return numstring without trailing 0 if is an integer."""
    number = float(numstring)
    return int(number) if number == int(number) else number
