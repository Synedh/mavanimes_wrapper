from django.utils import timezone
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

class Tag(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self) -> str:
        return self.name


class Anime(models.Model):
    name = models.CharField(max_length=1024)
    slug = models.SlugField(unique=True)
    image = models.URLField(null=True, default=None)
    small_image = models.URLField(null=True, default=None)
    tags = models.ManyToManyField(Tag)
    versions = models.CharField(max_length=128, null=True, default='')
    description = models.TextField(null=True, default='')
    update_date = models.DateTimeField(auto_now_add=True)
    mav_url = models.URLField()

    def __str__(self):
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('anime', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = 'Anime'
        verbose_name_plural = 'Animes'


class Episode(models.Model):
    name = models.CharField(max_length=1024)
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE)
    number = models.IntegerField(null=True, default=None)
    saison = models.IntegerField(null=True, default=1)
    version = models.CharField(max_length=128, null=True, default='VOSTFR')
    upload_date = models.DateTimeField(null=True, default=None)
    image = models.URLField(null=True, default=None)
    small_image = models.URLField(null=True, default=None)
    mav_url = models.URLField()

    def save(self, *args, **kwargs):
        anime_versions = set(*self.anime.version.split(',') + [self.version])
        self.anime.version = ','.join(sorted(list(anime_versions)))
        self.anime.update_date = timezone.now()
        if self.image and self.small_image:
            self.anime.image = self.image
            self.anime.small_image = self.image
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Episode'
        verbose_name_plural = 'Episodes'


class VideoURL(models.Model):
    url = models.URLField()
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.episode.name} - {self.url}'
