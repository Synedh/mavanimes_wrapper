import logging
import re
from typing import List

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from apps.animes.models import Anime, AnimeImage, Episode, VideoURL
from utils.parsers import get_page, parse_ep
from utils.utils import EpisodeDTO

logger = logging.getLogger(__name__)

def save_ep(episode_dict: EpisodeDTO) -> Episode:
    anime, new_anime = Anime.objects.get_or_create(slug=slugify(episode_dict['anime']))
    if new_anime:
        anime.name = episode_dict['anime']

    new_season = (
        episode_dict['season'] not in
        anime.episodes.values_list('season', flat=True).order_by().distinct()
    )
    video_urls = episode_dict['video_urls']
    del episode_dict['video_urls']
    if image := episode_dict.get('image'):
        del episode_dict['image']
    episode_dict['anime'] = anime

    if new_anime or new_season:
        logger.info('New %s: %s', 'season' if new_season else 'anime', anime.name)
        anime_image = AnimeImage(
            image=image,
            small_image=None,
            anime=anime,
            key=None if new_anime else f's{episode_dict["season"]}'
        )
        anime_image.save()

    episode, new_episode = Episode.objects.update_or_create(
        name=episode_dict['name'],
        anime=anime.id,
        version=episode_dict['version'],
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

def get_episode(url: str) -> Episode:
    episode = parse_ep(url)
    return save_ep(episode)

def anime_from_ep(url: str) -> List[Episode]:
    ep_html = get_page(url)
    ep_urls = re.findall(r'<option[^>]*value="(\S+)"', ep_html)
    return [get_episode(ep_url) for ep_url in ep_urls[::-1]]


class Command(BaseCommand):
    help = 'Get mavanimes episode'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='Episode url')
        parser.add_argument('-p', '--previous', type=bool, help='Add previous episodes too')

    def handle(self, *args, **options):
        if options['previous']:
            anime_from_ep(options['url'])
        else:
            get_episode(options['url'])
