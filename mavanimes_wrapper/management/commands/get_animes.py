from django.core.management.base import BaseCommand

import re
import json
import logging
import requests
from html.parser import HTMLParser

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

def html_to_anime(anime_html):
    anime_name = re.search(r'<h1 class="entry-title">(.*)</h1>', anime_html).group(1)
    image_html = re.search(r'<img .*?\/>', anime_html)
    images = []
    if image_html:
        images = re.findall(r'(https?://.*?)["\s]', image_html.group())

    try:
        description_html = re.search(r'<img .*?\/><br \/>(.*?)<(?:(?:h2)|(?:div))', anime_html, re.DOTALL).group(1)
    except AttributeError:
        description_html = re.search(r'INFORMATIONS DE L’ANIME</div>(.*?)<(?:(?:h2)|(?:div))', anime_html, re.DOTALL).group(1)
    HTML_CLEANER.feed(description_html)
    description = HTML_CLEANER.close().strip()

    tags_line = re.search(r'genres?\s?:(.*)', description, re.IGNORECASE).group(1)
    tags = [tag.strip() for tag in re.findall(r'[\w \'’\-]+', tags_line.lower())]

    return {
        'name': re.sub(r'(?:V[A-Z]+)|(?:Saison\s\d+)', '', anime_name).replace(' :', ':').strip(),
        'image': images[-1] if len(images) else None,
        'small_image': images[1] if len(images) > 1 else None,
        'tags': tags,
        'description': description,
        'version': re.search(r'V[A-Z]+', anime_name).group()
    }


def get_anime_url_list():
    response = requests.get('http://www.mavanimes.co/tous-les-animes-en-vostfr-fullhd-2/')
    return re.findall(r'<li>\s*<a href=\"(.*?)\">', response.text, re.MULTILINE)



def get_animes():
    anime_url_list = get_anime_url_list()
    for anime_url in anime_url_list[:1]:
        response = requests.get(anime_url)
        anime = {
            **html_to_anime(response.text),
            'mav_url': anime_url
        }
        logger.info(json.dumps(anime, indent=4))


class Command(BaseCommand):
    help = 'Get all mavanimes animes'

    def handle(self, *args, **options):
        get_animes()
