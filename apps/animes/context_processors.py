from .models import Anime

def anime_name_list(request):
    return {
        'anime_name_list': [anime['name'] for anime in Anime.objects.values('name')]
    }
