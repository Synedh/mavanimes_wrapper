import logging
import re
import requests
import dateutil.parser
from html import unescape

from apps.animes.models import Episode

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
    ep_name = unescape(ep_name)
    saison = next(iter(re.findall(r'saisons?\s?(\d+)', ep_name, flags=re.IGNORECASE)), 1)
    ep_name = re.sub(r'(\(\s*)?saisons?\s*\d+(\s*\))?', '', ep_name, flags=re.IGNORECASE)

    version = next(iter(re.findall(r'\W((?:VF)|(?:VOSTFR))', ep_name, re.IGNORECASE)), None)
    if version:
        ep_name = re.sub(version, '', ep_name)

    try:
        number = re.search(r'^.*?((?:\d*\.)?\d+)\D*$', ep_name).group(1)
        ep_name = re.sub(r'^(.*?)(?:\d*\.)?\d+(\D*)$', r'\1\2', ep_name)
    except AttributeError:
        number = '0'

    episode_type = Episode.Type.EPISODE
    splitted_name = ep_name.lower().split()
    if re.search(r'\bsp.ciale?\b', ep_name, re.IGNORECASE):
        episode_type = Episode.Type.SPECIAL
    elif 'film' in splitted_name or 'movie' in splitted_name:
        episode_type = Episode.Type.FILM
    elif 'oav' in splitted_name or 'ova' in splitted_name:
        episode_type = Episode.Type.OAV

    return {
        'anime': re.search(r'^\W*(.*?)[^a-zA-Z0-9)]*$', ep_name).group(1),
        'saison': int(saison),
        'number': float(number),
        'type': episode_type,
        'version': version
    }

def date_and_videos_of_ep(url):
    episode_html = get_page(url, allow_to_fail=True)
    if not episode_html:
        episode_html = ''
    pub_date = next(iter(re.findall(r'<meta property="article:published_time" content="(.*?)" />', episode_html)), None)
    return (
        dateutil.parser.parse(pub_date) if pub_date else None,
        re.findall(r'iframe.+?src="(.*?)"', episode_html)[:-1]
    )
