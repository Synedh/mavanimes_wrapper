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

    episodes = [{
        'name': 'foo',
        'upload_date': datetime(2022, 12, 13),
        'number': '0',
        'anime': {
            'slug': 'foo'
        }
    }, {
        'name': 'bar',
        'upload_date': datetime(2022, 12, 13),
        'number': '0',
        'anime': {
            'slug': 'bar'
        }
    }, {
        'name': 'test',
        'upload_date': datetime(2022, 12, 12),
        'number': '0',
        'anime': {
            'slug': 'test'
        }
    }]

    episodes_days = {}
    for i in range(7, 0, -1):
        date = (seven_days_ago + timedelta(days=i)).date() 
        episodes_days[date] = [
            episode for episode in episodes
            if episode['upload_date'].date() == date
        ]

    animes = ['foo', 'bar', 'test', 'toto']
    context = {
        'episodes_days': episodes_days,
        'last_animes': animes
        # 'last_animes': Anime.objects.order_by('-update_date').all()[:10]
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
