from rest_framework import viewsets, permissions

from apps.animes.models import Anime
from apps.animes.serializers import AnimeSerializer


class AnimeViewSet(viewsets.ModelViewSet):
    queryset = Anime.objects.all()
    serializer_class = AnimeSerializer
    permission_classes = [permissions.IsAuthenticated]
