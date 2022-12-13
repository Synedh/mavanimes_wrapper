from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'licencing'

urlpatterns = [
    path('', views.index, name='index'),
    path('animes/', views.anime_list, name='anime_list'),
    path('animes/<slug:slug>/', views.anime, name='anime_list'),
    path('animes/<slug:slug>/<int:number>/', views.episode, name='episode')
]
