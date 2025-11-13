from django.urls import path, include
from .views import get_article, update_sentiment, verify_article, add_tag, remove_tag, delete_article, verified_articles,set_tag_sentiment


urlpatterns = [

    path('get/', get_article, name='get_article'),
    path('<int:articleid>/article_sentiment/',
         update_sentiment, name='update_sentiment'),
    path('<int:articleid>/verify/',
         verify_article, name='verify_article'),
    path('<int:articleid>/add_tag/',
         add_tag, name='add_tag'),
    path('<int:articleid>/remove_tag/',
         remove_tag, name='remove_tag'),
    path('<int:articleid>/delete/',
         delete_article, name='delete_article'),
    path('verified/', verified_articles, name='verified_articles'),
    path('set_tag_sentiment/', set_tag_sentiment, name='set_tag_sentiment'),
    

]   