from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('animes', views.AnimeViewSet)

urlpatterns = [
    path('', include(router.urls))
]
