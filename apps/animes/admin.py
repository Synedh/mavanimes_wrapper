from django.contrib import admin

from .models import Tag, Anime, Episode, VideoURL

class EpisodeInline(admin.StackedInline):
    model = Episode
    extra = 0
    fields = ('name', 'number', 'saison', 'version', 'pub_date', 'mav_url')

class VideoURLInline(admin.TabularInline):
    model = VideoURL
    extra = 0
    fields = ('source', 'url')

class AnimeAdmin(admin.ModelAdmin):
    list_display = ('name', 'update_date')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'image', 'small_image', 'tags', 'versions', 'description', 'update_date', 'mav_url')
    readonly_fields = ('update_date',)
    autocomplete_fields = ('tags',)
    inlines = [EpisodeInline]


class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'saison', 'number', 'version')
    search_fields = ('name',)
    ordering = ('name',)
    fields = ('name', 'anime', 'number', 'saison', 'version', 'pub_date', 'mav_url')
    inlines = [VideoURLInline]


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fields = ('name',)

admin.site.register(Tag, TagAdmin)
admin.site.register(Anime, AnimeAdmin)
admin.site.register(Episode, EpisodeAdmin)
