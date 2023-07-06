from datetime import datetime, timedelta
from collections import defaultdict

from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import render, get_object_or_404

from utils.parsers import date_and_videos_of_ep
from .models import Anime, Episode, Tag, VideoURL


def index(request):
    seven_days_ago = timezone.make_aware(datetime.fromordinal(
        (timezone.now() - timedelta(days=7)).date().toordinal()
    ))
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

    if tag_names == ['']:
        animes_tags = Tag.objects.all()
    else:
        animes_tags = Tag.objects.filter(animes__in=animes).distinct()

    context = {
        'animes': Paginator(animes, limit).get_page(page),
        'search_tags': tags,
        'tags': animes_tags
    }
    return render(request, 'animes/anime_list.html', context)

def movie_list(request):
    limit = request.GET.get('limit', 100)
    page = request.GET.get('page')
    search = request.GET.get('search', '')
    movies = Episode.objects.filter(name__icontains=search, type=Episode.Type.FILM).order_by('name')

    context = {
        'movies': Paginator(movies, limit).get_page(page)
    }
    return render(request, 'animes/movie_list.html', context)

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
        key=lambda season: f'0{season["name"]}' if season['name'][0] == 'S' else season['name'])
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
        try:
            pub_date, video_urls = date_and_videos_of_ep(episode.mav_url)
            episode.pub_date = pub_date

            previous_video_urls = [video_url.url for video_url in episode.video_urls.all()]
            msg = 'No update required'
            if video_urls != previous_video_urls:
                episode.video_urls.all().delete()
                _ = [VideoURL.objects.get_or_create(
                    url=url,
                    source=url.split('.')[0].split('/')[-1],
                    episode=episode
                ) for url in video_urls]
                msg = 'Update done, please refresh the page.'
            episode.save()
            return HttpResponse(msg)
        except Exception as err:
            return HttpResponseServerError(err)
    else:
        raise Http404('Page not found')
