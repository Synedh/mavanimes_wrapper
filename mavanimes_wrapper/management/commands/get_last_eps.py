import re
import requests


def videos_of_ep(url):
    response = requests.get(url)
    if not response.ok:
        print(response.status_code, response.url)
        exit(1)

    return re.findall(r'iframe\s+src="(.*?)"', response.text)

def html_to_ep(ep_html):
    ep_name = re.search(r'<p>(.*?)<\/p>', ep_html).group(1)
    anime, saison, number, version = re.search(r'^(.*?)\–?\s?(?:\(\s?Saison\s?(\d+).*?)?(\d+)?\s?([a-zA-Z]*)$', ep_name).groups()
    url = re.search(r'<a href="(.*?)">', ep_html).group(1)

    return {
        'anime': anime,
        'saison': int(saison) if saison else 1,
        'number': int(number),
        'version': version,
        'name': ep_name,
        'video_urls': videos_of_ep(url),
        'mav_url': url,
        'image': re.search(r'src="(.*?)"', ep_html).group(1),
        'small_image': re.search(r'srcset=".*?(?:(http://.*?)\s.*?)+"', ep_html).group(1)
    }

def get_last_eps():
    response = requests.get('http://www.mavanimes.co/')
    if not response.ok:
        print(response.status_code, response.url)
        exit(1)

    eps_html = re.findall(r'<div class="col\-sm\-3 col\-xs\-12">(.+?)<\/div>', response.text.replace('\n', ' '))
    return [html_to_ep(ep_html) for ep_html in eps_html]