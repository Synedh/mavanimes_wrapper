from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('animes', views.AnimeViewSet)
router.register('episodes', views.EpisodeViewSet)
router.register('video_url', views.VideoURLViewSet)

urlpatterns = [
    path('', include(router.urls))
]
