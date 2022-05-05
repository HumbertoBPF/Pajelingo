from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name = 'index'),
    path('vocabulary_game/setup', views.vocabulary_game_setup, name = 'vocabulary_game_setup'),
    path('vocabulary_game/verify_answer', views.vocabulary_game_verify_answer, name = 'vocabulary_game_verify_answer'),
    path('vocabulary_game', views.vocabulary_game, name = 'vocabulary_game'),
    path('article_game/setup', views.article_game_setup, name = 'article_game_setup'),
    path('article_game', views.article_game, name = 'article_game'),
    path('article_game/verify_answer', views.article_game_verify_answer, name = 'article_game_verify_answer')
]
