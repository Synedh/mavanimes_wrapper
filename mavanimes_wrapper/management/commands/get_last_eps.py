import logging
import re
import xml.etree.ElementTree

import dateutil.parser
from django.core.management.base import BaseCommand

from apps.animes.models import Anime, Episode, VideoURL
from utils.parsers import ep_title_parser, get_page

logger = logging.getLogger(__name__)
URL = 'http://www.mavanimes.co/'


def get_anime_images(anime, homepage):
    res = re.search(rf'<a href="{anime.episodes.last().mav_url}">.*?src="(.*?)".*?srcset=".*?(?:(https?://.*?)\s.*?)+"', homepage, re.DOTALL)
    return res.group(1), res.group(2)

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

def save_ep(episode_dict, homepage):
    anime, new_anime = Anime.objects.get_or_create(name=episode_dict['anime'])
    video_urls = episode_dict['video_urls']
    del episode_dict['video_urls']
    episode_dict['anime'] = anime

    episode, new_episode = Episode.objects.update_or_create(
        name=episode_dict['name'], anime=anime.id,
        defaults={**episode_dict}
    )
    if new_anime:
        image, small_image = get_anime_images(anime, homepage)
        anime.image = image
        anime.small_image = small_image
        anime.save()

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

def get_last_eps():
    feed = xml.etree.ElementTree.fromstring(get_page(f'{URL}feed/'))
    episodes = [parse_ep(xml_ep) for xml_ep in feed[0].findall('item')]
    return [save_ep(episode, get_page(URL)) for episode in episodes]

class Command(BaseCommand):
    help = 'Get last mavanimes episodes'

    def handle(self, *args, **options):
        get_last_eps()
