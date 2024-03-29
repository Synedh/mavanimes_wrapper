import logging
import re
from typing import Any

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.animes.models import Anime, Episode, VideoURL
from utils.parsers import ep_title_parser

logger = logging.getLogger(__name__)


def videos_of_ep(url: str) -> list[str]:
    response = requests.get(url, timeout=5000)
    if not response.ok:
        logger.error(
            'HTTP Error %d while requesting %s: %s',
            response.status_code, response.url, response.text
        )
        exit(1)

    return re.findall(r'iframe\s+src="(.*?)"', response.text)

def html_to_ep(ep_html: str) -> dict[str, Any]:
    ep_name = re.search(r'<p>(.*?)<\/p>', ep_html).group(1)
    url = re.search(r'<a href="(.*?)">', ep_html).group(1)

    logger.info(ep_name)
    episode = ep_title_parser(ep_name)

    return {
        'anime': episode['anime'],
        'saison': episode['saison'],
        'number': episode['number'],
        'version': episode['version'],
        'name': ep_name,
        'video_urls': videos_of_ep(url),
        'mav_url': url,
        'image': re.search(r'src="(.*?)"', ep_html).group(1),
        'small_image': re.search(r'srcset=".*?(?:(http://.*?)\s.*?)+"', ep_html).group(1)
    }

def save_ep(episode_dict: dict[str, Any]) -> Episode:
    anime, _ = Anime.objects.update_or_create(
        name=episode_dict['anime'],
        defaults={
            'image': episode_dict['image'],
            'small_image': episode_dict['small_image']
        }
    )
    video_urls = episode_dict['video_urls']
    del episode_dict['video_urls']
    del episode_dict['image']
    del episode_dict['small_image']
    episode_dict['anime'] = anime

    episode, new_episode = Episode.objects.update_or_create(
        name=episode_dict['name'], anime=anime.id,
        defaults={**episode_dict}
    )
    videos = [VideoURL.objects.get_or_create(
        url=url,
        source=url.split('.')[0].split('/')[-1],
        episode=episode
    ) for url in video_urls]

    if new_episode or any(new_url for _, new_url in videos):
        logger.info('%s episode %s', "New" if new_episode else "Updated", episode.name)
        episode.upload_date = timezone.now()
        episode.save()
    return episode

def get_last_eps() -> list[Episode]:
    response = requests.get('http://www.mavanimes.co/', timeout=5000)
    if not response.ok:
        logger.error(
            'HTTP Error %d while requesting %s: %s',
            response.status_code, response.url, response.text
        )
        exit(1)

    eps_html = re.findall(r'<div class="col\-sm\-3 col\-xs\-12">(.+?)<\/div>', response.text.replace('\n', ' '))
    episodes = [html_to_ep(ep_html) for ep_html in eps_html]
    return [save_ep(episode) for episode in episodes]

class Command(BaseCommand):
    help = 'Get last mavanimes episodes'

    def handle(self, *args, **options):
        get_last_eps()
