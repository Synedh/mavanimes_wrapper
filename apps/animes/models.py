from django.utils import timezone
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

class Tag(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self) -> str:
        return self.name


class Anime(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    slug = models.SlugField(unique=True)
    image = models.URLField(blank=True, null=True, default=None)
    small_image = models.URLField(blank=True, null=True, default=None)
    tags = models.ManyToManyField(Tag, blank=True)
    versions = models.CharField(max_length=128, blank=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    update_date = models.DateTimeField(auto_now_add=True)
    mav_url = models.URLField(blank=True, null=True, default='')

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('anime', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = 'Anime'
        verbose_name_plural = 'Animes'


class Episode(models.Model):
    name = models.CharField(max_length=1024)
    value = models.CharField(max_length=128)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='episodes')
    number = models.IntegerField(blank=True, null=True, default=None)
    saison = models.IntegerField(blank=True, null=True, default=1)
    version = models.CharField(max_length=128, blank=True, null=True, default='VOSTFR')
    upload_date = models.DateTimeField(blank=True, null=True, default=None)
    image = models.URLField(blank=True, null=True, default=None)
    small_image = models.URLField(blank=True, null=True, default=None)
    mav_url = models.URLField()

    def save(self, *args, **kwargs):
        anime_versions = set(self.anime.versions.split(',')) | set([self.version])
        self.anime.versions = ','.join(sorted(v for v in list(anime_versions) if v))
        self.anime.update_date = timezone.now()
        if self.image and self.small_image:
            self.anime.image = self.image
            self.anime.small_image = self.image
        self.anime.save()
        self.value = f'{self.saison}x{self.number}'
        return super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('episode', kwargs={'value': self.value})

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['number', 'saison', 'version', 'anime__name']
        verbose_name = 'Episode'
        verbose_name_plural = 'Episodes'


class VideoURL(models.Model):
    url = models.URLField()
    source = models.CharField(max_length=1024)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='video_urls')

    def __str__(self) -> str:
        return f'{self.source} - {self.url}'

    class Meta:
        ordering = ['-episode__id']
        verbose_name = 'Video URL'
        verbose_name_plural = 'Video URLs'
