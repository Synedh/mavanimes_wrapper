from django.urls import path

from . import views

app_name = 'animes'

urlpatterns = [
    path('', views.index, name='index'),
    path('animes/', views.anime_list, name='anime_list'),
    path('animes/<slug:slug>/', views.anime_detail, name='anime_detail'),
    path('animes/<slug:anime_slug>/<slug:episode_slug>/', views.episode_detail, name='episode'),
    path('animes/<slug:anime_slug>/<slug:episode_slug>/refresh/', views.refresh_episode, name='refresh_episode')
]
