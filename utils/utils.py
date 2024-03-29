import logging
from datetime import datetime
from typing import Optional, TypedDict

from apps.animes.models import Anime, Episode

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
    video_urls: list[str]
    mav_url: str


def move_anime(old_id: int, new_id: int, season: int | None=1, delete: bool | None=False) -> None:
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
