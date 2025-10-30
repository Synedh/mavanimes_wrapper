from typing import Callable
import uuid

from django.http import HttpRequest, HttpResponse

def correlation_id(
    get_response: Callable[[HttpRequest], HttpResponse]
) -> Callable[[HttpRequest], HttpResponse]:

    def middleware(request: HttpRequest) -> HttpResponse:
        id = uuid.uuid4()
        request.META['correlation_id'] = id
        response = get_response(request)
        return response
    
    return middleware
