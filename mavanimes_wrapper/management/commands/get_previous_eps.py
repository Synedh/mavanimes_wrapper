from django.core.management.base import BaseCommand

from datetime import datetime, timezone
import logging
import re
import requests

from .parsers import ep_title_parser
from apps.animes.models import Anime, Episode, VideoURL

logger = logging.getLogger(__name__)


def videos_of_ep(url):
    response = requests.get(url)
    if not response.ok:
        logger.error(f'HTTP Error {response.status_code} while requesting {response.url}: {response.text}')
        exit(1)

    return re.findall(r'iframe\s+src="(.*?)"', response.text)


def get_eps_of_ep(ep_url):
    response = requests.get(ep_url)
    if not response.ok:
        logger.error(f'HTTP Error {response.status_code} while requesting {response.url}: {response.text}')
        exit(1)

    episodes = re.findall(r'<option.*? value="(.*?)">(.*?)</option>', response.text)[1:]
    return [(name, url, videos_of_ep(url)) for url, name in episodes]


def get_all_eps(anime):
    logger.info(anime.name)
    last_ep_url = anime.episodes.get(number=10, saison=3).mav_url
    registered_eps = [anime.name for anime in anime.episodes.all()]

    episodes = []
    for ep_name, mav_url, video_urls in get_eps_of_ep(last_ep_url):
        if ep_name in registered_eps:
            continue
        episode = ep_title_parser(ep_name)
        episodes.append({
            'anime': episode['anime'],
            'saison': episode['saison'],
            'number': episode['number'],
            'version': episode['version'],
            'name': ep_name,
            'video_urls': video_urls,
            'mav_url': mav_url,
            'image': anime.image,
            'small_image': anime.small_image
        })
    return episodes

def save_ep(anime, episode_dict):
    video_urls = episode_dict['video_urls']
    del episode_dict['video_urls']
    episode_dict['anime'] = anime

    episode = Episode(
        **episode_dict,
        upload_date=datetime(1970, 1, 1, tzinfo=timezone.utc)
    )
    episode.save()

    [VideoURL.objects.get_or_create(
        url=url,
        source=url.split('.')[0].split('/')[-1],
        episode=episode
    ) for url in video_urls]
    return episode


def get_last_eps():
    response = requests.get('http://www.mavanimes.co/')
    if not response.ok:
        logger.error(f'HTTP Error {response.status_code} while requesting {response.url}: {response.text}')
        exit(1)

    anime = Anime.objects.get(name='Mairimashita! Iruma-kun')
    episodes = get_all_eps(anime)
    return [save_ep(anime, episode) for episode in episodes]

class Command(BaseCommand):
    help = 'Get last mavanimes episodes'

    def handle(self, *args, **options):
        get_last_eps()
