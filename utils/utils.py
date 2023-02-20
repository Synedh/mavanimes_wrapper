from apps.animes.models import Anime, Episode

def move_anime(old_id, new_id, season=1):
    old_anime = Anime.objecs.find(id=old_id)
    new_anime = Anime.objects.find(id=new_id)
    Episode.objects.filter(anime=old_anime).update(anime=new_anime, season=season)
    new_anime.episodes.first().save()
    # old_anime.delete()
