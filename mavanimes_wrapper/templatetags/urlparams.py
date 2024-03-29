from urllib.parse import urlencode

from django import template

register = template.Library()

@register.simple_tag
def urlparams(*_, **kwargs) -> str:
    safe_args = { key: value for key, value in kwargs.items() if value != '' }
    return f'?{format(urlencode(safe_args))}' if safe_args else ''
