from datetime import datetime

import colorfield.fields

from django.utils import timezone
from django.contrib import admin
from django.db import models
from django.db.models.functions import Upper
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

class Tag(models.Model):
    name = models.CharField(max_length=1024)
    color = colorfield.fields.ColorField()

    def save(self, *args, **kwargs):
        hashed = hash(self.name)
        color = lambda i: (hashed >> i * 8) % 255 # pylint: disable=unnecessary-lambda-assignment
        self.color = f'#{color(0):02x}{color(1):02x}{color(2):02x}'
        return super().save(*args, **kwargs)

    def __str__(self) -> str: # pylint: disable=invalid-str-returned
        return self.name

    @property
    @admin.display(description='Quantity of animes')
    def qty_animes(self) -> int:
        return Anime.objects.filter(tags__id=self.id).count()

    @property
    @admin.display(description='Animes')
    def list_animes(self) -> str:
        """ Used by admin to display tags usage """
        return '\n'.join(anime.name for anime in Anime.objects.filter(tags__id=self.id))

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Anime(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    slug = models.SlugField(unique=True)
    image = models.URLField(blank=True, null=True, default=None)
    small_image = models.URLField(blank=True, null=True, default=None)
    tags = models.ManyToManyField(Tag, blank=True, related_name='animes')
    versions = models.CharField(max_length=128, blank=True, default='')
    episodes_count = models.IntegerField(default=0)
    description = models.TextField(blank=True, default='')
    update_date = models.DateTimeField(auto_now_add=True)
    mav_url = models.URLField(blank=True, default='')

    def __str__(self) -> str: # pylint: disable=invalid-str-returned
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('animes:anime_detail', kwargs={'slug': self.slug})

    def get_images(self, key: str | None=None) -> "AnimeImage":
        try:
            return self.images.get(key=key)
        except ObjectDoesNotExist:
            return self.images.first() # pylint: disable=no-member

    def save(self, *args, **kwargs) -> None:
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = [Upper('name')]
        verbose_name = 'Anime'
        verbose_name_plural = 'Animes'


class AnimeImage(models.Model):
    image = models.URLField(blank=True, null=True, default=None)
    small_image = models.URLField(blank=True, null=True, default=None)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='images')
    key = models.CharField(max_length=128, blank=True, null=True, default=None)

    class Meta:
        ordering = ['key']
        constraints = [
            models.UniqueConstraint(fields=['anime', 'key'], name='unique_anime_key')
        ]


class Episode(models.Model):
    class Type(models.TextChoices):
        EPISODE = 'EPISODE'
        FILM = 'FILM'
        OAV = 'OAV'
        SPECIAL = 'SPECIAL'

    name = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=128)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='episodes')
    type = models.CharField(max_length=7, choices=Type.choices, blank=True, default=Type.EPISODE)
    number = models.FloatField(blank=True, null=True, default=None)
    season = models.IntegerField(blank=True, default=1)
    version = models.CharField(max_length=128, blank=True, default='VOSTFR')
    pub_date = models.DateTimeField(blank=True,
        default=datetime(1970, 1, 1, tzinfo=timezone.get_current_timezone()))
    mav_url = models.URLField()

    def image(self) -> str | None:
        key = f's{self.season}'
        if self.type != self.Type.EPISODE:
            key = f'{self.type.lower()}{self.number}' # pylint: disable=no-member
        images = self.anime.get_images(key)
        if not images:
            return None
        return images.small_image if images.small_image else images.image

    def save(self, *args, **kwargs) -> None:
        self.slug = f'{self.version.lower()}-{self.type.lower()}-{self.season}-{self.number:g}' # pylint: disable=no-member
        super().save(*args, **kwargs)
        anime_versions = set(self.anime.versions.split(',')) | set([self.version]) # pylint: disable=no-member
        self.anime.versions = ','.join(sorted(v for v in list(anime_versions) if v))
        self.anime.episodes_count = self.anime.episodes.count()
        self.anime.save()

    def delete(self, *args, **kwargs) -> None:
        super().delete(*args, **kwargs)
        self.anime.versions = ','.join(
            self.anime.episodes
                .values_list('version', flat=True)
                .order_by('version')
                .distinct()
        )
        self.anime.episodes_count = self.anime.episodes.count()
        self.anime.save()

    def get_absolute_url(self) -> str:
        return reverse(
            'animes:episode',
            kwargs={
                'anime_slug': self.anime.slug,
                'ep_slug': self.slug
            }
        )

    def __str__(self) -> str: # pylint: disable=invalid-str-returned
        return self.name

    class Meta:
        ordering = ['season', 'number', 'version', 'anime__name']
        verbose_name = 'Episode'
        verbose_name_plural = 'Episodes'


class VideoURL(models.Model):
    url = models.URLField()
    source = models.CharField(max_length=1024)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='video_urls')

    def __str__(self) -> str:
        return f'{self.source} - {self.url}'

    def save(self, *args, **kwargs) -> None:
        self.source = self.url.split('/')[2].split('.')[-2] # pylint: disable=no-member
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-episode__id']
        verbose_name = 'Video URL'
        verbose_name_plural = 'Video URLs'
