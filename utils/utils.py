import logging
from typing import TypedDict, List, Optional
from datetime import datetime

from apps.animes.models import Anime, Episode, VideoURL

logger = logging.getLogger(__name__)

class EpisodeDTO(TypedDict):
        anime: str
        season: int
        number: float
        type: Episode.Type
        version: str
        name: str
        image: Optional[str]
        small_image: Optional[str]
        pub_date: datetime
        video_urls: List[str]
        mav_url: str

## TODO ##
def save_episode(episode_dict: EpisodeDTO) -> Episode:
    anime, new_anime = Anime.objects.get_or_create(name=episode_dict['anime'])
    video_urls = episode_dict['video_urls']
    del episode_dict['video_urls']
    episode_dict['anime'] = anime

    if new_anime:
        logger.info('New anime %s', anime.name)

    episode, new_episode = Episode.objects.update_or_create(
        name=episode_dict['name'], anime=anime.id,
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


def move_anime(old_id, new_id, season=1, delete=False):
    old_anime = Anime.objects.get(id=old_id)
    new_anime = Anime.objects.get(id=new_id)
    old_images = old_anime.get_images()
    for episode in old_anime.episodes.all():
        episode.anime = new_anime
        episode.season = season
        episode.save()
    if old_images and old_images.image != new_anime.get_images().image:
        old_images.anime = new_anime
        old_images.key = f's{season}'
        old_images.save()
    if delete:
        old_anime.delete()
