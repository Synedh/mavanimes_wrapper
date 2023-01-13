from rest_framework import serializers

from .models import Anime, Episode, VideoURL

class VideoURLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VideoURL
        fields = '__all__'

class AnimeSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name'
    )

    class Meta:
        model = Anime
        fields = [
            'url', 'tags', 'name', 'image', 'small_image', 'versions',
            'episodes', 'episodes_count', 'description',  'update_date',
            'mav_url'
        ]

class EpisodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Episode
        fields = [
            'url', 'name', 'type', 'number', 'season', 'version', 'pub_date',
            'mav_url', 'anime', 'video_urls'
        ]
