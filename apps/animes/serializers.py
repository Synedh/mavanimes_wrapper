from rest_framework import serializers

from .models import Anime, Episode, VideoURL

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class VideoURLSerializer(DynamicFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VideoURL
        fields = '__all__'


class AnimeSerializer(DynamicFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
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


class EpisodeSerializer(DynamicFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Episode
        fields = [
            'url', 'name', 'type', 'number', 'season', 'version', 'pub_date',
            'mav_url', 'anime', 'video_urls'
        ]
