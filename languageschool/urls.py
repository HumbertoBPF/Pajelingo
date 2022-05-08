from django.urls import path
from languageschool import views

urlpatterns = [
    path('', views.general.index, name = 'index'),
    path('vocabulary_game/setup', views.vocabulary_game.vocabulary_game_setup, name = 'vocabulary_game_setup'),
    path('vocabulary_game/verify_answer', views.vocabulary_game.vocabulary_game_verify_answer, name = 'vocabulary_game_verify_answer'),
    path('vocabulary_game', views.vocabulary_game.vocabulary_game, name = 'vocabulary_game'),
    path('article_game/setup', views.article_game.article_game_setup, name = 'article_game_setup'),
    path('article_game', views.article_game.article_game, name = 'article_game'),
    path('article_game/verify_answer', views.article_game.article_game_verify_answer, name = 'article_game_verify_answer'),
    path('conjugation_game/setup', views.conjugation_game.conjugation_game_setup, name = 'conjugation_game_setup'),
    path('conjugation_game', views.conjugation_game.conjugation_game, name = 'conjugation_game'),
    path('conjugation_game/verify_answer', views.conjugation_game.conjugation_game_verify_answer, name = 'conjugation_game_verify_answer'),
    path('search', views.general.search, name = 'search')
]
