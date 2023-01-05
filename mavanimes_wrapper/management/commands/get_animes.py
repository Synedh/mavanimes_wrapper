from django.core.management.base import BaseCommand

import re
import logging
from html import unescape
from html.parser import HTMLParser

from apps.animes.models import Anime, Episode, VideoURL, Tag
from .parsers import date_and_videos_of_ep, ep_title_parser, get_page

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
        episodes_html = re.findall(r'<a (?:title=".*?" )?href="(.*?)">• (.*?)<', anime_html)

    total = len(episodes_html)
    episodes = []
    for i, (mav_url, name) in enumerate(episodes_html, start=1):
        logger.info(f'[{i}/{total}] {name}')
        episode = ep_title_parser(name)
        pub_date, video_urls = date_and_videos_of_ep(mav_url)
        episodes.append({
            'season': episode['season'],
            'number': episode['number'],
            'type': episode['type'],
            'version': episode['version'].upper() if episode['version'] else None,
            'name': name,
            'pub_date': pub_date,
            'video_urls': video_urls,
            'mav_url': mav_url
        })

    next_page = next(iter(re.findall(r'<a.*?href="(.*?)".*?>Next.*?</a>', anime_html)), None)
    if next_page:
        anime_html = get_page(next_page)
        episodes += html_to_episodes(anime_html)

    ep_eps = [ep for ep in episodes if ep['type'] == Episode.Type.EPISODE]
    if (
        len(ep_eps) and
        max(ep['season'] for ep in ep_eps) == 1 and
        max(ep['number'] for ep in ep_eps) != len(ep_eps)
    ):
        input(f'\aInvalid number of eps. Max num: {max(ep["number"] for ep in ep_eps)}, nb eps: {len(ep_eps)}')
    return episodes

def url_to_anime(anime_url):
    anime_html = get_page(anime_url)
    anime_name = unescape(re.search(r'<h1 class="entry-title">(.*)</h1>', anime_html).group(1))
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
    anime_name = ' '.join(re.sub(r'(?:V[A-Z]+)|(?:\(?S(?:aison\s)?\d+\s*\)?)', '', anime_name).replace(' :', ':').split())
    logger.info(f'Anime: {anime_name}')

    return (
        {
            'name': anime_name,
            'image': images[-1] if len(images) else None,
            'small_image': images[1] if len(images) > 1 else None,
            'tags': tags,
            'description': description,
            'mav_url': anime_url
        },
        html_to_episodes(anime_html)
    )

def save_anime(anime_dict, episodes_list):
    tags = anime_dict['tags']
    del anime_dict['tags']
    anime, new_anime = Anime.objects.update_or_create(
        name=anime_dict["name"],
        defaults={**anime_dict}
    )
    anime.tags.add(*[Tag.objects.get_or_create(name=tag)[0] for tag in tags])
    logger.info(f'{"New" if new_anime else "Updating"} anime {anime.name}')

    for episode_dict in episodes_list:
        video_urls = episode_dict['video_urls']
        del episode_dict['video_urls']
        episode_dict['anime'] = anime

        episode, new_episode = Episode.objects.update_or_create(
            name=episode_dict['name'], anime=anime,
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


def get_anime_url_list():
    anime_urls_html = get_page('http://www.mavanimes.co/tous-les-animes-en-vostfr-fullhd-2/')
    return re.findall(r'<li>\s*<a href=\"(.*?)\">', anime_urls_html, re.MULTILINE)

def get_animes(start=0):
    anime_url_list = get_anime_url_list()
    total = len(anime_url_list)
    for i, anime_url in enumerate(anime_url_list[start:], start=start + 1):
        anime, episodes = url_to_anime(anime_url)
        if not anime:
            logger.info(f'[{i}/{total}] Skipped {anime_url}')
            continue
        logger.info(f'[{i}/{total}] {anime["name"]} - {len(episodes)} episode(s)')
        save_anime(anime, episodes)


class Command(BaseCommand):
    help = 'Get all mavanimes animes'

    def handle(self, *args, **options):
        get_animes(1334)
