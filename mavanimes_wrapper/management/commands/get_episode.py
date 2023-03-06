import logging
import re
from typing import List, Union

from django.core.management.base import BaseCommand

from apps.animes.models import Anime, Episode, VideoURL
from utils.parsers import get_page, parse_ep
from utils.utils import EpisodeDTO

logger = logging.getLogger(__name__)

def save_ep(episode_dict: EpisodeDTO) -> Episode:
    anime, new_anime = Anime.objects.get_or_create(name=episode_dict['anime'])
    video_urls = episode_dict['video_urls']
    del episode_dict['video_urls']
    episode_dict['anime'] = anime

    if new_anime:
        logger.info('New anime %s', anime.name)

    episode, new_episode = Episode.objects.update_or_create(
        name=episode_dict['name'], anime=anime.id,
        defaults={**episode_dict}
    )

    previous_video_urls = [video_url.url for video_url in episode.video_urls.all()]
    if video_urls != previous_video_urls:
        episode.video_urls.all().delete()
        _ = [VideoURL.objects.get_or_create(
            url=url,
            source=url.split('.')[0].split('/')[-1],
            episode=episode
        ) for url in video_urls]
    logger.info('%s episode %s', "New" if new_episode else "Updated", episode.name)
    return episode

def get_episode(url: str) -> Union[Episode, None]:
    try:
        return parse_ep(url)
    except Exception as err:
        logger.error(err)
        return None

def anime_from_ep(url: str) -> List[Union[Episode, None]]:
    ep_html = get_page(url)
    ep_urls = re.findall(r'<option[^>]*value="(\S+)"', ep_html)
    return [get_episode(ep_url) for ep_url in ep_urls[::-1]]


class Command(BaseCommand):
    help = 'Get last mavanimes episodes'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--previous', type=bool, help='Add previous episodes too')
        parser.add_argument('-u', '--url', type=str, help='Episode url')

    def handle(self, *args, **options):
        if options['previous']:
            anime_from_ep(options['url'])
        else:
            get_episode(options['url'])