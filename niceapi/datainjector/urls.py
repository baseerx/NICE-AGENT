from django.urls import path
from .views import set_session


urlpatterns = [
    path('session/', set_session, name='set_session'),
]
