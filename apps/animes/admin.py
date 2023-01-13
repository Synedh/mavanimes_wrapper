from django.contrib import admin

from .models import Tag, Anime, Episode, VideoURL

class EpisodeInline(admin.StackedInline):
    model = Episode
    extra = 0
    fields = ('name', 'type', 'number', 'season', 'version', 'pub_date', 'mav_url')

class VideoURLInline(admin.TabularInline):
    model = VideoURL
    extra = 0
    fields = ('source', 'url')

class AnimeAdmin(admin.ModelAdmin):
    list_display = ('name', 'episodes_count', 'update_date')
    search_fields = ('name',)
    ordering = ('name', 'episodes_count', 'update_date')
    fields = ('name', 'image', 'small_image', 'tags', 'versions', 'description', 'update_date', 'mav_url', 'episodes_count')
    readonly_fields = ('update_date', 'episodes_count')
    autocomplete_fields = ('tags',)
    inlines = [EpisodeInline]


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'pub_date', 'season', 'number', 'version')
    search_fields = ('name',)
    ordering = ('name', 'pub_date')
    fields = ('name', 'anime', 'type', 'number', 'season', 'version', 'pub_date', 'mav_url')
    inlines = [VideoURLInline]

class VideoAdmin(admin.ModelAdmin):
    list_display = ('url', 'source')
    search_fields = ('source', 'url')
    pass

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'qty_animes')
    search_fields = ('name',)
    fields = ('name', 'color', 'qty_animes', 'list_animes')
    readonly_fields = ('qty_animes', 'list_animes')

admin.site.register(Tag, TagAdmin)
admin.site.register(VideoURL, VideoAdmin)
admin.site.register(Anime, AnimeAdmin)
admin.site.register(Episode, EpisodeAdmin)
