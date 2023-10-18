from datetime import datetime, timedelta
from collections import defaultdict

from django.utils import timezone
from django.utils.safestring import SafeText
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, Http404, HttpResponseServerError
from django.shortcuts import render, get_object_or_404

from utils.parsers import date_and_videos_of_ep
from .models import Anime, Episode, Tag, VideoURL


def index(request: HttpRequest) -> HttpResponse:
    seven_days_ago = timezone.make_aware(datetime.fromordinal(
        (timezone.now() - timedelta(days=6)).date().toordinal()
    ))
    episodes = (
        Episode.objects.filter(pub_date__gte=seven_days_ago)
                       .order_by('-pub_date')
    )

    episodes_days = []
    for i in range(6, -1, -1):
        date = (seven_days_ago + timedelta(days=i)).date()
        eps = [
            episode for episode in episodes
            if episode.pub_date.date() == date
        ]
        episodes_days.append([date, eps])

    context = {
        'episodes_days': episodes_days
    }
    return render(request, 'index.html', context)

def anime_list(request: HttpRequest) -> HttpResponse:
    limit = request.GET.get('limit', '100')
    page = request.GET.get('page')
    search = request.GET.get('search', '')
    tag_names = request.GET.getlist('tags', '')

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

def movie_list(request: HttpRequest) -> HttpResponse:
    limit = request.GET.get('limit', '100')
    page = request.GET.get('page')
    search = request.GET.get('search', '')
    movies = Episode.objects.filter(name__icontains=search, type=Episode.Type.FILM).order_by('name')

    context = {
        'movies': Paginator(movies, limit).get_page(page)
    }
    return render(request, 'animes/movie_list.html', context)

def anime_detail(request: HttpRequest, slug: SafeText) -> HttpResponse:
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

def episode_detail(request: HttpRequest, anime_slug: SafeText, ep_slug: SafeText) -> HttpResponse:
    episode = get_object_or_404(Episode, anime__slug=anime_slug, slug=ep_slug)
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

def refresh_episode(request: HttpRequest, anime_slug: SafeText, ep_slug: SafeText) -> HttpResponse:
    if request.method == 'PATCH':
        episode = get_object_or_404(Episode, anime__slug=anime_slug, slug=ep_slug)
        try:
            pub_date, video_urls = date_and_videos_of_ep(episode.mav_url)
            episode.pub_date = pub_date

            previous_video_urls = [video_url.url for video_url in episode.video_urls.all()]
            if video_urls == previous_video_urls:
                return HttpResponse('No update required')
            episode.video_urls.all().delete()
            _ = [VideoURL.objects.get_or_create(
                url=url,
                source=url.split('.')[0].split('/')[-1],
                episode=episode
            ) for url in video_urls]
            episode.save()
            return HttpResponse('Update done, please refresh the page.')
        except Exception as err: # pylint: disable=broad-exception-caught
            return HttpResponseServerError(err)
    else:
        raise Http404('Page not found')

def calendar(request: HttpRequest) -> HttpResponse:
    today = timezone.make_aware(datetime.fromordinal(datetime.now().date().toordinal()))
    animes_week_1 = set(episode.anime for episode in Episode.objects.filter(
        pub_date__lt=today,
        pub_date__gte=today - timedelta(days=8)
    ))
    animes_week_2 = set(episode.anime for episode in Episode.objects.filter(
        pub_date__lt=today - timedelta(days=7),
        pub_date__gte=today - timedelta(days=15)
    ))

    animes = animes_week_1.intersection(animes_week_2)
    days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    weekdays_animes = [
        (
            days[weekday],
            [anime for anime in animes if anime.episodes.last().pub_date.weekday() == weekday]
        ) for weekday in range(7)
    ]

    context = {
        'today': days[today.weekday()],
        'weekdays_animes': weekdays_animes
    }
    return render(request, 'animes/calendar.html', context)
