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
    path('search', views.general.search, name = 'search'),
    path('dictionary/<int:word_id>', views.general.dictionary, name = 'dictionary'),
    path('account/signin', views.account.sign_in, name = 'account_sign_in'),
    path('account/create_user', views.account.create_user, name = 'account_create_user'),
    path('account/login', views.account.login, name = 'account_login'),
    path('account/auth_user', views.account.auth_user, name = 'account_auth_user'),
    path('account/logout', views.account.logout, name = 'account_logout'),
    path('account/profile', views.account.profile, name = 'account_profile'),
    path('account/update_user', views.account.update_user, name = 'account_update_user'),
    path('account/do_update_user', views.account.do_update_user, name = 'account_do_update_user'),
    path('account/delete_user', views.account.delete_user, name = 'account_delete_user'),
    path('rankings', views.general.rankings, name = 'rankings')
]
