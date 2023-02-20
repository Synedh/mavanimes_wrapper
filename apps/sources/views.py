import re

import requests

from django.http import HttpResponse, HttpResponseBadRequest

def streamtape(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponseBadRequest('Bad Request')
    page = requests.get(url, timeout=5000).text
    line = re.search(r'robotlink\'\).innerHTML.*', page).group()
    print(url, line)
    extract = re.sub(r".*?(//.*?)\W{3,}\w{3}(.*?)\W{3}.*", r"\1\2", line)
    return HttpResponse(f'https:{extract}&stream=1')
