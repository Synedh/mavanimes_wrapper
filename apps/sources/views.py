import re

import requests

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotAllowed)
from django.views.decorators.cache import cache_page


@cache_page(60)
def streamtape(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponseBadRequest('Bad Request')
    page = requests.get(url, timeout=5000).text
    line = re.search(r'robotlink\'\).innerHTML.*', page).group()
    extract = re.sub(r".*?(//.*?)\W{3,}\w{3}(.*?)\W{3}.*", r"\1\2", line)
    if 'id=WP9OOGyY8Xtb3Am&' in extract:
        return HttpResponseNotAllowed('Streamtape blocked the request')

    return HttpResponse(f'https:{extract}&stream=1')
