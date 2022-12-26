from django.urls import path

from languageschool import views
from languageschool.views.games import vocabulary_game, article_game, conjugation_game
from languageschool.views.viewsets import GameViewSet, ArticleViewSet, CategoryViewSet, ConjugationViewSet, \
    LanguageViewSet, MeaningViewSet, ScoreListViewSet, ScoreViewSet, WordViewSet, UserViewSet

urlpatterns = [
    path('dashboard', views.general.index, name='index'),
    path('vocabulary-game/setup', vocabulary_game.setup, name='vocabulary-game-setup'),
    path('vocabulary-game', vocabulary_game.play, name='vocabulary-game'),
    path('vocabulary-game/verify-answer', vocabulary_game.verify_answer, name='vocabulary-game-verify-answer'),
    path('article-game/setup', article_game.setup, name='article-game-setup'),
    path('article-game', article_game.play, name='article-game'),
    path('article-game/verify-answer', article_game.verify_answer, name='article-game-verify-answer'),
    path('conjugation-game/setup', conjugation_game.setup, name='conjugation-game-setup'),
    path('conjugation-game', conjugation_game.play, name='conjugation-game'),
    path('conjugation-game/verify-answer', conjugation_game.verify_answer, name='conjugation-game-verify-answer'),
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
    path('activate/<uidb64>/<token>', views.account.activate, name='account-activate'),
    path('rankings', views.general.rankings, name='rankings'),
    path('account/change-picture', views.account.change_picture, name='account-change-picture'),
    path('api/games', GameViewSet.as_view(), name='games-api'),
    path('api/languages/', LanguageViewSet.as_view(), name='languages-api'),
    path('api/categories/', CategoryViewSet.as_view(), name='categories-api'),
    path('api/articles/', ArticleViewSet.as_view(), name='articles-api'),
    path('api/words/', WordViewSet.as_view(), name='words-api'),
    path('api/meanings/', MeaningViewSet.as_view(), name='meanings-api'),
    path('api/conjugations/', ConjugationViewSet.as_view(), name='conjugations-api'),
    path('api/user/', UserViewSet.as_view(), name='user-api'),
    path('api/score/', ScoreViewSet.as_view(), name='score-api'),
    path('api/score/<int:score_id>', ScoreViewSet.as_view(), name='update-score-api'),
    path('api/scores/', ScoreListViewSet.as_view(), name='scores-api')
]
