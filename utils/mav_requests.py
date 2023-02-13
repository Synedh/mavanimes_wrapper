import logging

import requests

logger = logging.getLogger(__name__)

def get_page(url, allow_to_fail=False):
    response = requests.get(url, timeout=5000)
    if not response.ok and not allow_to_fail:
        logger.error(
            'HTTP Error %d while requesting %s: %s',
            response.status_code, response.url, response.text
        )
        exit(1)
    elif not response.ok:
        return None
    return response.text