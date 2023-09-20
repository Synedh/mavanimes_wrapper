from django.urls import path

from . import views

app_name = 'animes'

urlpatterns = [
    path('', views.anime_list, name='anime_list'),
    path('calendar/', views.calendar, name='calendar'),
    path('<slug:slug>/', views.anime_detail, name='anime_detail'),
    path('<slug:anime_slug>/<str:ep_slug>/', views.episode_detail, name='episode'),
    path('<slug:anime_slug>/<str:ep_slug>/refresh/', views.refresh_episode, name='refresh_episode')
]
