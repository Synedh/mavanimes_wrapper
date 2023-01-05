from django.core.management.base import BaseCommand

import dateutil.parser
import logging
import re
import xml.etree.ElementTree as ET

from .parsers import ep_title_parser, get_page
from apps.animes.models import Anime, Episode, VideoURL

logger = logging.getLogger(__name__)


def get_anime_images(anime):
    anime.save()

def parse_ep(ep_xml):
    name = ep_xml.find('title').text
    date = ep_xml.find('pubDate').text
    link = ep_xml.find('link').text
    content = ep_xml.find(r'{http://purl.org/rss/1.0/modules/content/}encoded').text
    episode = ep_title_parser(name)

    return {
        'anime': episode['anime'],
        'season': episode['season'],
        'number': episode['number'],
        'version': episode['version'],
        'name': name,
        'video_urls': re.findall(r'iframe\s+src="(.*?)"', content),
        'mav_url': link,
        'pub_date': dateutil.parser.parse(date)
    }

def save_ep(episode_dict):
    anime, new_anime = Anime.objects.get_or_create(name=episode_dict['anime'])
    if new_anime:
        get_anime_images(anime)

    video_urls = episode_dict['video_urls']
    del episode_dict['video_urls']
    episode_dict['anime'] = anime

    episode, new_episode = Episode.objects.update_or_create(
        name=episode_dict['name'], anime=anime.id,
        defaults={**episode_dict}
    )

    previous_video_urls = [video_url.url for video_url in episode.video_urls.all()]
    if video_urls != previous_video_urls:
        episode.video_urls.all().delete()
        [VideoURL.objects.get_or_create(
            url=url,
            source=url.split('.')[0].split('/')[-1],
            episode=episode
        ) for url in video_urls]
        logger.info(f'{"New" if new_episode else "Updated"} episode {episode.name}')
    return episode

def get_last_eps():
    homepage = get_page('http://www.mavanimes.co/')
    eps_html = re.findall(r'<div class="col\-sm\-3 col\-xs\-12">(.+?)<\/div>', homepage.replace('\n', ' '))
    feed = ET.fromstring(get_page('http://www.mavanimes.co/feed/'))
    episodes = [parse_ep(xml_ep) for xml_ep in feed[0].findall('item')]
    return [save_ep(episode) for episode in episodes]

class Command(BaseCommand):
    help = 'Get last mavanimes episodes'

    def handle(self, *args, **options):
        get_last_eps()
