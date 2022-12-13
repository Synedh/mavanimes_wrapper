from django.contrib import admin

from .models import Tag, Anime, Episode, VideoURL

class EpisodeInline(admin.StackedInline):
    model = Episode
    extra = 0
    fields = ('name', 'image', 'number', 'saison', 'upload_date')

class VideoURLInline(admin.StackedInline):
    model = VideoURL
    extra = 0
    fields = ('url',)

class AnimeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'tags')
    ordering = ('name',)
    fields = ('name', 'image', 'small_image', 'tags', 'description', 'mav_url')
    autocomplete_fields = ('tags',)
    inlines = [EpisodeInline]


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'saison', 'number')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'anime', 'number', 'saison', 'version', 'upload_date', 'image', 'small_image', 'mav_url')
    inlines = [VideoURLInline]


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fields = ('name',)

admin.site.register(Tag, TagAdmin)
admin.site.register(Anime, AnimeAdmin)
admin.site.register(Episode, EpisodeAdmin)
