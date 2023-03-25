import logging
import re
from typing import List
from html import unescape
from html.parser import HTMLParser

from django.db import IntegrityError
from django.core.management.base import BaseCommand

from apps.animes.models import Anime, Episode, AnimeImage, Tag
from mavanimes_wrapper.management.commands.get_episode import save_ep
from utils.parsers import get_page, parse_ep
from utils.utils import EpisodeDTO

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

def html_to_episodes(anime_html: str, anime_name: str) -> List[EpisodeDTO]:
    episodes_html = re.findall(r'<h2 class="raees "><a href="(.*?)">:• &nbsp;&nbsp;(.*?)</a></h2>', anime_html)
    if not episodes_html:
        episodes_html = re.findall(r'<div>(?:<strong>)?<a title=".*?" href="(.*?)">(?:<strong>)?• (.*?)(?:</strong>)?</a>(?:</strong>)?</div>', anime_html)
    if not episodes_html:
        episodes_html = re.findall(r'<a (?:title=".*?" )?href="(.*?)">• (.*?)<', anime_html)

    total = len(episodes_html)
    episodes: List[EpisodeDTO] = []
    for i, (mav_url, name) in enumerate(episodes_html, start=1):
        logger.info(f'[{i}/{total}] {name}')
        episode = {
            **parse_ep(mav_url),
            'anime': anime_name,
            'name': name
        }
        del episode['image']
        episodes.append(episode)

    next_page = re.search(r'<a.*?href="(.*?)".*?>Next.*?</a>', anime_html)
    if next_page:
        anime_html = get_page(next_page.group(1))
        episodes += html_to_episodes(anime_html, anime_name)

    ep_eps = [ep for ep in episodes if ep['type'] == Episode.Type.EPISODE]
    if (
        len(ep_eps) and
        max(ep['season'] for ep in ep_eps) == 1 and
        max(ep['number'] for ep in ep_eps) != len(ep_eps)
    ):
        input(f'\aInvalid number of eps. Max num: {max(ep["number"] for ep in ep_eps)}, nb eps: {len(ep_eps)}')
    return episodes

def html_to_anime(anime_html: str) -> dict:
    anime_name = unescape(re.search(r'<h1 class="entry-title">(.*)</h1>', anime_html).group(1))
    logger.info(f'Anime: {anime_name}')
    anime_name = ' '.join(re.sub(r'(?:V[A-Z]+)|(?:\(?S(?:aison\s)?\d+\s*\)?)', '', anime_name).replace(' :', ':').split())
    anime_name = re.search(r'^\W*(.*?)[^a-zA-Z0-9)]*$', anime_name).group(1)

    image_html = re.search(r'<img .*?\/>', anime_html)
    images = []
    if image_html:
        images = re.findall(r'(https?://.*?)["\s]', image_html.group())

    try:
        description_html = re.search(r'<img .*?\/><br \/>(.*?)<(?:(?:h2)|(?:div))', anime_html, re.DOTALL + re.IGNORECASE).group(1)
    except AttributeError:
        try:
            description_html = re.search(r'INFORMATIONS D.*?</div>(.*?)<(?:(?:h2)|(?:div))', anime_html, re.DOTALL).group(1)
        except AttributeError as e:
            logger.error(e)
            input('\a')
            return None, []
    HTML_CLEANER.feed(description_html)
    description = HTML_CLEANER.close().strip()

    tags_line = re.search(r'genre\(?s?\)?\s?:(.*)', description, re.IGNORECASE).group(1) if 'genre' in description.lower() else ''
    tags = [tag.strip() for tag in re.findall(r'[\w \'’\-]+', tags_line.lower())]

    return {
        'name': anime_name,
        'image': images[-1] if len(images) else None,
        'small_image': images[1] if len(images) > 1 else None,
        'tags': tags,
        'description': description
    }

def get_anime(url: str) -> Anime:
    anime_html = get_page(url)
    anime_dict = html_to_anime(anime_html)
    episodes_dict = html_to_episodes(anime_html, anime_dict['name'])
    episodes = [save_ep(episode) for episode in episodes_dict]
    if not episodes:
        return None
    anime = episodes[0].anime
    if not anime.description:
        anime.description = anime_dict['description']
        anime.tags.add(*[Tag.objects.get_or_create(name=tag)[0] for tag in anime_dict['tags']])
    if not anime.mav_url:
        anime.mav_url = url
    try:
        anime.save()
        _, _ = AnimeImage.objects.get_or_create(
            image=anime_dict['image'],
            small_image=anime_dict['small_image'],
            anime=anime,
            key=f's{episodes[0].season}'
        )
    except IntegrityError:
        pass
    return anime


class Command(BaseCommand):
    help = 'Get mavanimes anime'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--url', type=str, help='Anime url')

    def handle(self, *args, **options):
        get_anime(options['url'])
