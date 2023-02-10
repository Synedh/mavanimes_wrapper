from datetime import datetime, timedelta
from collections import defaultdict

from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404

from .models import Anime, Episode, Tag

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
    limit = request.GET.get('limit', 100)
    page = request.GET.get('page')
    search = request.GET.get('search', '')
    tag_names = request.GET.get('tags', '').split(',')

    tags = Tag.objects.filter(name__in=tag_names)
    animes = Anime.objects.filter(name__icontains=search)
    for tag in tags:
        animes = animes.filter(tags=tag)
    paginator = Paginator(animes, limit)
    context = {
        'animes': paginator.get_page(page),
        'search_tags': tags
    }
    return render(request, 'animes/anime_list.html', context)

def anime_detail(request, slug):
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
            versions[episode.version][f'Saison {episode.season}'].append(episode)

    content = {
        version: sorted([{
            'name': ep_type,
            'values': val
        } for ep_type, val in values.items()],
        key=lambda season: ('0' if season["name"][0] == 'S' else '') + season["name"])
        for version, values in versions.items()
    }

    context = {
        'anime': anime,
        'seasons': anime.episodes.latest('season').season if anime.episodes.count() else 0,
        'versions': content
    }
    return render(request, 'animes/anime_detail.html', context)

def episode_detail(request, anime_slug, episode_slug):
    episode = get_object_or_404(Episode, anime__slug=anime_slug, slug=episode_slug)
    episode = get_object_or_404(Episode, anime__slug=anime_slug, slug=episode_slug)
    episode_index = list(episode.anime.episodes.all()).index(episode)

    previous_ep, next_ep = None, None
    if episode_index > 0:
        previous_ep = episode.anime.episodes.all()[episode_index - 1].slug
    if episode_index < episode.anime.episodes.count() - 1:
        next_ep = episode.anime.episodes.all()[episode_index + 1].slug

    context = {
        'episode': episode,
        'previous': previous_ep,
        'next': next_ep
    }
    return render(request, 'animes/episode.html', context)

def refresh_episode(request, anime_slug, episode_slug):
    if request.method == 'PATCH':
        episode = get_object_or_404(Episode, anime__slug=anime_slug, slug=episode_slug)
        return HttpResponse('OK')
    else:
        raise Http404('Page not found')
