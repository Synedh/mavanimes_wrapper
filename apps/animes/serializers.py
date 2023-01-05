from django.db.models import Max
from rest_framework import serializers

from .models import Anime

class AnimeSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    qty_episodes = serializers.SerializerMethodField()
    qty_seasons = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_qty_episodes(self, anime):
        return anime.episodes.count()

    def get_qty_seasons(self, anime):
        return anime.episodes.latest('season').season if anime.episodes.count() else 0

    def get_image(self, anime):
        return anime.small_image if anime.small_image else anime.image

    class Meta:
        model = Anime
        fields = [
            'name',
            'slug',
            'image',
            'versions',
            'qty_episodes',
            'qty_seasons',
            'tags'
        ]
