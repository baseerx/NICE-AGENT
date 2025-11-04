from django.urls import path
from .views import register, login_view, session_check, user_logout
urlpatterns = [
    # path('admin/', admin.site.urls), 
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('session/', session_check, name='session_check'),
    path('logout/', user_logout, name='logout'),
]