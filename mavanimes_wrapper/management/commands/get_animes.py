import logging
import re

from django.core.management.base import BaseCommand

from mavanimes_wrapper.management.commands.get_anime import get_anime
from utils.parsers import get_page

logger = logging.getLogger(__name__)


def get_anime_url_list(url):
    anime_urls_html = get_page(url)
    return re.findall(r'<li>\s*<a href=\"(.*?)\">', anime_urls_html, re.MULTILINE)

def get_animes(url, start=0):
    anime_url_list = get_anime_url_list(url)
    total = len(anime_url_list)
    for i, anime_url in enumerate(anime_url_list[start:], start=start + 1):
        anime = get_anime(anime_url)
        if not anime:
            logger.info('[%d/%d] Skipped %s', i, total, anime_url)
            continue
        logger.info('[%d/%d] %s - %s episode(s)', i, total, anime.name, anime.episodes.count())


class Command(BaseCommand):
    help = 'Get all animes from mavanimes url'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--url', type=str, help='Episode url')

    def handle(self, *args, **options):
        get_animes(options['url'])
