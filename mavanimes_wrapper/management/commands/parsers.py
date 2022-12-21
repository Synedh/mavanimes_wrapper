import logging
import re
import requests

logger = logging.getLogger(__name__)

def get_page(url, allow_to_fail=False):
    response = requests.get(url)
    if not response.ok and not allow_to_fail:
        logger.error(f'HTTP Error {response.status_code} while requesting {response.url}: {response.text}')
        exit(1)
    elif not response.ok:
        return None
    return response.text


def ep_title_parser(ep_name):
    saison = next(iter(re.findall(r'saisons?\s?(\d+)', ep_name, flags=re.IGNORECASE)), 1)
    ep_name = re.sub(r'(\(\s*)?saisons?\s*\d+(\s*\))?', '', ep_name, flags=re.IGNORECASE)

    version = next(iter(re.findall(r'\W((?:VF)|(?:VOSTFR))', ep_name, re.IGNORECASE)), None)
    if version:
        ep_name = re.sub(version, '', ep_name)

    try:
        number = re.search(r'^.*?(\d+)\D*$', ep_name).group(1)
        ep_name = re.sub(r'^(.*?)\d+\D*$', r'\1', ep_name)
    except AttributeError:
        if 'film' in ep_name.lower():
            number = '-1'
            ep_name = re.sub(r'film', '', ep_name, flags=re.IGNORECASE)
        else:
            number = '0'

    return {
        'anime': re.search(r'^\W*(.*?)[^a-zA-Z0-9)]*$', ep_name).group(1),
        'saison': int(saison),
        'number': int(number),
        'version': version
    }

def videos_of_ep(url):
    episode_html = get_page(url, allow_to_fail=True)
    return re.findall(r'iframe\s+src="(.*?)"', episode_html) if episode_html else []
