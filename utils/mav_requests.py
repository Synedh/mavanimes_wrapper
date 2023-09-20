from typing import Union

import requests

def get_page(url: str, allow_to_fail: bool=False) -> Union[str, None]:
    response = requests.get(url, timeout=5000)
    if not response.ok and not allow_to_fail:
        raise ValueError(f'HTTP Error {response.status_code} while requesting {response.url}')
    elif not response.ok:
        return None
    return response.text
