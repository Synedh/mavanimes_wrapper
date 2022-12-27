from django.utils import timezone
from django.shortcuts import render, get_object_or_404

from datetime import datetime, timedelta
from collections import defaultdict

from .models import Anime, Episode

def index(request):
    seven_days_ago = timezone.make_aware(datetime(*(timezone.now().date() - timedelta(days=7)).timetuple()[:6]))
    episodes = (
        Episode.objects.filter(pub_date__gte=seven_days_ago)
                       .order_by('pub_date')
    )

    episodes_days = []
    for i in range(7, 0, -1):
        date = (seven_days_ago + timedelta(days=i)).date()
        eps = sorted([episode for episode in episodes
            if episode.pub_date.date() == date
        ], key=lambda episode: episode.pub_date, reverse=True)
        episodes_days.append([date, eps])

    context = {
        'episodes_days': episodes_days,
        'last_animes': Anime.objects.order_by('-update_date').all()[:10]
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
    versions = {version: defaultdict(list) for version in anime.versions.split(',')}

    for episode in anime.episodes.all():
        if episode.type == Episode.Type.SPECIAL:
            versions[episode.version]['Episodes speciaux'].append(episode)
        elif episode.type == Episode.Type.FILM:
            versions[episode.version]['Films'].append(episode)
        elif episode.type == Episode.Type.OAV:
            versions[episode.version]['OAV'].append(episode)
        else:
            versions[episode.version][f'Saison {episode.saison}'].append(episode)
    
    for saisons in versions.values():
        # Disable defaultdict tools to be able to iterate in template
        saisons.default_factory = None

    context = {
        'anime': anime,
        'saisons': anime.episodes.latest('saison').saison if anime.episodes.count() else 0,
        'versions': versions
    }
    return render(request, 'animes/anime_detail.html', context)

def episode(request, slug, value):
    episode = get_object_or_404(Episode, anime__slug=slug, value=value)
    episode_index = list(episode.anime.episodes.all()).index(episode)

    previous_value, next_value = None, None
    if episode_index > 0:
        previous_value = episode.anime.episodes.all()[episode_index - 1].value
    if episode_index < episode.anime.episodes.count() - 1:
        next_value = episode.anime.episodes.all()[episode_index + 1].value

    context = {
        'episode': episode,
        'previous_value': previous_value,
        'next_value': next_value
    }
    return render(request, 'animes/episode.html', context)
