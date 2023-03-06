from apps.animes.models import Anime

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
