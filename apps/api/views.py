from rest_framework import viewsets
from rest_framework.settings import api_settings

from apps.animes.models import Anime, Episode, VideoURL
from apps.animes.serializers import AnimeSerializer, EpisodeSerializer, VideoURLSerializer


class PageSizeViewSet(viewsets.ModelViewSet):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    pagination_class.page_size_query_param = 'limit'
    http_method_names = ['get']


class AnimeViewSet(PageSizeViewSet):
    queryset = Anime.objects.all()
    serializer_class = AnimeSerializer


class EpisodeViewSet(PageSizeViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer


class VideoURLViewSet(PageSizeViewSet):
    queryset = VideoURL.objects.all()
    serializer_class = VideoURLSerializer
