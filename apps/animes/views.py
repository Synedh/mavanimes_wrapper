from django.utils import timezone
from django.shortcuts import render, get_object_or_404

from datetime import datetime, timedelta

from .models import Anime, Episode

def index(request):
    seven_days_ago = timezone.make_aware(datetime(*(timezone.now().date() - timedelta(days=7)).timetuple()[:6]))
    episodes = (
        Episode.objects.filter(upload_date__lte=seven_days_ago)
                       .order_by('upload_date')
    )

    context = {
        'episodes': episodes
    }
    return render(request, 'index.html', context)

def anime_list(request):
    animes = Anime.objects.all().order_by('name')

    context = {
        'animes': animes
    }
    return render(request, 'animes/anime_list.html', context)

def anime(request, slug):
    anime = get_object_or_404(Anime, slug=slug)

    context = {
        'anime': anime
    }
    return render(request, 'animes/anime_detail.html', context)

def episode(request, slug, number):
    episode = get_object_or_404(Episode, anime__slug=slug, number=number)

    context = {
        'episode': episode
    }
    return render(request, 'animes/episode.html', context)
