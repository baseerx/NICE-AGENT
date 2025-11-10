from django.urls import path, include
from .views import get_article


urlpatterns = [path('get/', get_article, name='get_article')]   