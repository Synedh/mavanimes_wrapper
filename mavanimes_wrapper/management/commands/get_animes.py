from django.core.management.base import BaseCommand

import re
import logging
from html.parser import HTMLParser

from .parsers import videos_of_ep, ep_title_parser, get_page

logger = logging.getLogger(__name__)

class HTMLCleaner(HTMLParser):
    text = ''

    def handle_data(self, data: str):
        self.text += data

    def close(self):
        super().close()
        text = self.text
        self.text = ''
        return text


HTML_CLEANER = HTMLCleaner()

def html_to_episodes(anime_html):
    episodes_html = re.findall(r'<h2 class="raees "><a href="(.*?)">:• &nbsp;&nbsp;(.*?)</a></h2>', anime_html)
    if not episodes_html:
        episodes_html = re.findall(r'<div>(?:<strong>)?<a title=".*?" href="(.*?)">(?:<strong>)?• (.*?)(?:</strong>)?</a>(?:</strong>)?</div>', anime_html)
    if not episodes_html:
        episodes_html = re.findall(r'<a href="(.*?)">• (.*?)(?:</a>)?<br />', anime_html)
    if not episodes_html:
        input('No episode')

    episodes = []
    for mav_url, name in episodes_html:
        print(name)
        episode = ep_title_parser(name)
        episodes.append({
            'saison': episode['saison'],
            'number': episode['number'],
            'version': episode['version'],
            'name': name,
            'video_urls': videos_of_ep(mav_url),
            'mav_url': mav_url
        })
    return episodes

def html_to_anime(anime_html):
    anime_name = re.search(r'<h1 class="entry-title">(.*)</h1>', anime_html).group(1)
    image_html = re.search(r'<img .*?\/>', anime_html)
    images = []
    if image_html:
        images = re.findall(r'(https?://.*?)["\s]', image_html.group())

    try:
        description_html = re.search(r'<img .*?\/><br \/>(.*?)<(?:(?:h2)|(?:div))', anime_html, re.DOTALL).group(1)
    except AttributeError:
        try:
            description_html = re.search(r'INFORMATIONS D.*?</div>(.*?)<(?:(?:h2)|(?:div))', anime_html, re.DOTALL).group(1)
        except AttributeError as e:
            logger.error(e)
            input()
            return None
    HTML_CLEANER.feed(description_html)
    description = HTML_CLEANER.close().strip()

    tags_line = re.search(r'genres?\s?:(.*)', description, re.IGNORECASE).group(1) if 'genres' in description.lower() else ''
    tags = [tag.strip() for tag in re.findall(r'[\w \'’\-]+', tags_line.lower())]

    episodes = html_to_episodes(anime_html)

    return {
        'name': ' '.join(re.sub(r'(?:V[A-Z]+)|(?:\(?S(?:aison\s)?\d+\)?)', '', anime_name).replace(' :', ':').split()),
        'image': images[-1] if len(images) else None,
        'small_image': images[1] if len(images) > 1 else None,
        'tags': tags,
        'description': description,
        'version': next(iter(re.findall(r'V[A-Z]+', anime_name)), None),
        'episodes': episodes
    }

def get_anime_url_list():
    anime_urls_html = get_page('http://www.mavanimes.co/tous-les-animes-en-vostfr-fullhd-2/')
    return re.findall(r'<li>\s*<a href=\"(.*?)\">', anime_urls_html, re.MULTILINE)

def get_animes():
    anime_url_list = get_anime_url_list()
    total = len(anime_url_list)
    for i, anime_url in enumerate(anime_url_list[95:], start=96):
        anime = html_to_anime(get_page(anime_url))
        if not anime:
            logger.info(f'[{i}/{total}] Skipped {anime_url}')
            continue
        anime = {**anime, 'mav_url': anime_url}
        logger.info(f'[{i}/{total}] {anime["name"]} - {len(anime["episodes"])} episode(s)')


class Command(BaseCommand):
    help = 'Get all mavanimes animes'

    def handle(self, *args, **options):
        get_animes()
