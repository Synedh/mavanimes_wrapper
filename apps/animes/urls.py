from django.urls import path

from . import views

app_name = 'animes'

urlpatterns = [
    path('', views.index, name='index'),
    path('animes/', views.anime_list, name='anime_list'),
    path('animes/<slug:slug>/', views.anime_detail, name='anime_detail'),
    path('animes/<slug:slug>/<str:value>/', views.episode, name='episode')
]
