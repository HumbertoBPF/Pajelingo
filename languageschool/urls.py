from django.urls import path

from languageschool import views
from languageschool.views.games import vocabulary_game, article_game, conjugation_game
from languageschool.views.viewsets import GameViewSet, ArticleViewSet, CategoryViewSet, ConjugationViewSet, \
    LanguageViewSet, MeaningViewSet, ScoreListViewSet, ScoreViewSet, WordViewSet

urlpatterns = [
    path('dashboard', views.general.index, name='index'),
    path('vocabulary-game/setup', vocabulary_game.VocabularyGame.setup, name='vocabulary-game-setup'),
    path('vocabulary-game', vocabulary_game.VocabularyGame.play, name='vocabulary-game'),
    path('vocabulary-game/verify-answer', vocabulary_game.VocabularyGame.verify_answer,
         name='vocabulary-game-verify-answer'),
    path('article-game/setup', article_game.ArticleGame.setup, name='article-game-setup'),
    path('article-game', article_game.ArticleGame.play, name='article-game'),
    path('article-game/verify-answer', article_game.ArticleGame.verify_answer, name='article-game-verify-answer'),
    path('conjugation-game/setup', conjugation_game.ConjugationGame.setup, name='conjugation-game-setup'),
    path('conjugation-game', conjugation_game.ConjugationGame.play, name='conjugation-game'),
    path('conjugation-game/verify-answer', conjugation_game.ConjugationGame.verify_answer,
         name='conjugation-game-verify-answer'),
    path('search', views.general.search, name='search'),
    path('dictionary/<int:word_id>', views.general.dictionary, name='dictionary'),
    path('account/signin', views.account.sign_in, name='account-sign-in'),
    path('account/create-user', views.account.create_user, name='account-create-user'),
    path('account/login', views.account.login, name='account-login'),
    path('account/auth-user', views.account.auth_user, name='account-auth-user'),
    path('account/logout', views.account.logout, name='account-logout'),
    path('account/profile', views.account.profile, name='account-profile'),
    path('account/update-user', views.account.update_user, name='account-update-user'),
    path('account/do-update-user', views.account.do_update_user, name='account-do-update-user'),
    path('account/delete-user', views.account.delete_user, name='account-delete-user'),
    path('rankings', views.general.rankings, name='rankings'),
    path('account/change-picture', views.account.change_picture, name='account-change-picture'),
    path('api/games', GameViewSet.as_view()),
    path('api/languages/', LanguageViewSet.as_view()),
    path('api/categories/', CategoryViewSet.as_view()),
    path('api/articles/', ArticleViewSet.as_view()),
    path('api/words/', WordViewSet.as_view()),
    path('api/meanings/', MeaningViewSet.as_view()),
    path('api/conjugations/', ConjugationViewSet.as_view()),
    path('api/scores/', ScoreListViewSet.as_view()),
    path('api/scores/<int:score_id>', ScoreViewSet.as_view())
]
