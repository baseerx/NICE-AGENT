from django.urls import path
from .views import register, login,session_view
urlpatterns = [
    # path('admin/', admin.site.urls), 
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('session/', session_view, name='session_view'),
]