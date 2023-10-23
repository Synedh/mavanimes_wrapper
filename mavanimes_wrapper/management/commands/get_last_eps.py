import logging
import re
import xml.etree.ElementTree

import dateutil.parser
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from apps.animes.models import Anime, AnimeImage, Episode, VideoURL
from utils.parsers import ep_title_parser, get_page
from utils.utils import EpisodeDTO

logger = logging.getLogger(__name__)
URL = 'http://www.mavanimes.co/'


def get_anime_images(anime: Anime, homepage: str) -> tuple[str]:
    res = re.search(rf'<a href="{anime.episodes.last().mav_url}">.*?src="(.*?)".*?srcset=".*?(?:(https?://.*?)\s.*?)+"', homepage, re.DOTALL)
    if res:
        return res.group(1), res.group(2)
    logger.warning('No image found for episode %s', anime.episodes.last().name)
    return None, None

def parse_ep(ep_xml: xml.etree.ElementTree.Element) -> EpisodeDTO:
    name = ep_xml.find('title').text
    date = ep_xml.find('pubDate').text
    link = ep_xml.find('link').text
    content = ep_xml.find(r'{http://purl.org/rss/1.0/modules/content/}encoded').text
    episode = ep_title_parser(name)

    return {
        **episode,
        'video_urls': re.findall(r'iframe\s+src="(.*?)"', content),
        'mav_url': link,
        'pub_date': dateutil.parser.parse(date)
    }

def save_ep(episode_dict: EpisodeDTO, homepage: str) -> Episode:
    anime, new_anime = Anime.objects.get_or_create(slug=slugify(episode_dict['anime']))
    if new_anime:
        anime.name = episode_dict['anime']

    new_season = (
        episode_dict['season'] not in
        anime.episodes.values_list('season', flat=True).order_by().distinct()
    )
    video_urls = episode_dict['video_urls']
    del episode_dict['video_urls']
    episode_dict['anime'] = anime

    episode, new_episode = Episode.objects.update_or_create(
        name=episode_dict['name'], anime=anime.id,
        defaults={**episode_dict}
    )
    if new_anime or new_season:
        image, small_image = get_anime_images(anime, homepage)
        anime_image = AnimeImage(
            image=image,
            small_image=small_image,
            anime=anime,
            key=None if new_anime else f's{episode.season}'
        )
        anime_image.save()

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

def get_last_eps() -> list[Episode]:
    feed = xml.etree.ElementTree.fromstring(get_page(f'{URL}feed/'))
    homepage = get_page(URL)
    episodes = [parse_ep(xml_ep) for xml_ep in feed[0].findall('item')]
    return [save_ep(episode, homepage) for episode in episodes]

class Command(BaseCommand):
    help = 'Get last mavanimes episodes'

    def handle(self, *args, **options):
        get_last_eps()
