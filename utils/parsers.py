import logging
import re
import json
from html import unescape

import dateutil.parser

from apps.animes.models import Episode
from utils.mav_requests import get_page
from utils.utils import EpisodeDTO

logger = logging.getLogger(__name__)

def ep_title_parser(ep_name):
    name = unescape(ep_name)
    parsed_name = unescape(ep_name)
    season_list = re.findall(r'saison?\s?(\d+)', parsed_name, flags=re.IGNORECASE)
    if season_list:
        parsed_name = re.sub(r'(\(\s*)?saison?\s*\d+(\s*\))?', '', parsed_name, flags=re.IGNORECASE)

    version = next(iter(re.findall(r'\W((?:VF)|(?:VOSTFR))', parsed_name, re.IGNORECASE)), None)
    if version:
        parsed_name = re.sub(version, '', parsed_name)

    try:
        number = float(re.search(r'^.*?((?:\d*\.)?\d+)\D*$', parsed_name).group(1))
        parsed_name = re.sub(r'^(.*?)(?:\d*\.)?\d+(\D*)$', r'\1\2', parsed_name)
    except AttributeError:
        number = 0.0

    episode_type = Episode.Type.EPISODE
    splitted_name = parsed_name.lower().split()
    if re.search(r'\bsp.ciale?s?\b', parsed_name, re.IGNORECASE) or 'sp' in splitted_name:
        episode_type = Episode.Type.SPECIAL
    elif 'film' in splitted_name or 'movie' in splitted_name:
        episode_type = Episode.Type.FILM
        parsed_name = re.sub('film|movie', '', parsed_name, re.IGNORECASE)
    elif 'oav' in splitted_name or 'ova' in splitted_name or 'OAV-' in parsed_name:
        episode_type = Episode.Type.OAV

    anime = re.search(r'^\W*(.*?)[^a-zA-Z0-9)]*$', parsed_name).group(1)
    if not season_list and (groups := re.search(r'\s+(\d+)$', anime)) and (season := int(groups.group())) < 21:
        anime = re.sub(r'\s+\d+$', '', anime)
    else:
        season = int(next(iter(season_list), 1))

    return {
        'name': name,
        'anime': anime,
        'season': season,
        'number': number,
        'type': episode_type,
        'version': version.upper()
    }

def date_and_videos_of_ep(url: str):
    episode_html = get_page(url, allow_to_fail=True)
    if not episode_html:
        return None, []
    pub_date = next(iter(re.findall(
        r'<meta property="article:published_time" content="(.*?)" />',
        episode_html
    )), None)
    return (
        dateutil.parser.parse(pub_date) if pub_date else None,
        re.findall(r'iframe.+?src="(.*?)"', episode_html)[:-1]
    )

def parse_ep(url: str) -> EpisodeDTO:
    episode_html = get_page(url)
    schema = json.loads(re.search(
        r'<script type=\'application\/ld\+json\'.*?>(.*?)</script>',
        episode_html
    ).group(1))
    pub_date = next(iter(re.findall(
        r'<meta property="article:published_time" content="(.*?)" />',
        episode_html
    )), None)
    return {
        **ep_title_parser(schema['@graph'][2]['headline']),
        'image': schema['@graph'][1].get('image', {}).get('url', None),
        'pub_date': dateutil.parser.parse(pub_date) if pub_date else None,
        'video_urls': re.findall(r'iframe.+?src="(.*?)"', episode_html)[:-1],
        'mav_url': url
    }
