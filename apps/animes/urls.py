from django.urls import path

from . import views

app_name = 'animes'

urlpatterns = [
    path('', views.anime_list, name='anime_list'),
    path('<slug:slug>/', views.anime_detail, name='anime_detail'),
    path('<slug:anime_slug>/<str:episode_slug>/', views.episode_detail, name='episode'),
    path('<slug:anime_slug>/<str:episode_slug>/refresh/', views.refresh_episode, name='refresh_episode')
]
