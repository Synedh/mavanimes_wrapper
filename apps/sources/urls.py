from django.urls import path

from . import views

app_name = 'sources'

urlpatterns = [
    path('streamtape/', views.streamtape, name='streamtape'),
]
