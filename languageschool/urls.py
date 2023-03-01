from django.urls import path

from languageschool import views
from languageschool.views.account import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from languageschool.views.api import SearchView, MeaningView, WordView
from languageschool.views.games import vocabulary_game, article_game, conjugation_game
from languageschool.views.viewsets import GameViewSet, ArticleViewSet, CategoryViewSet, ConjugationViewSet, \
    LanguageViewSet, MeaningViewSet, ScoreListViewSet, ScoreViewSet, WordViewSet, UserViewSet, PublicImageViewSet, \
    ResetPasswordViewSet, RankingsViewSet

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
    path('about-us', views.general.about_us, name='about-us'),
    path('meaning/<int:word_id>', views.general.meaning, name='meaning'),
    path('search-done', views.general.search_done, name='search-done'),
    path('account/signup', views.account.signup, name='signup'),
    path('account/login', views.account.login, name='login'),
    path('account/logout', views.account.logout, name='logout'),
    path('account/profile', views.account.profile, name='profile'),
    path('account/update-user', views.account.update_user, name='update-user'),
    path('account/delete-user', views.account.delete_user, name='delete-user'),
    path('account/activate/<uidb64>/<token>', views.account.activate, name='activate-account'),
    path('account/request-reset-account', PasswordResetView.as_view(), name='request-reset-account'),
    path('account/request-reset-account-done', PasswordResetDoneView.as_view(), name='request-reset-account-done'),
    path('account/reset-account/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='reset-account'),
    path('account/reset-account-done', PasswordResetCompleteView.as_view(), name='reset-account-done'),
    path('rankings', views.general.rankings, name='rankings'),
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
    path('api/scores/', ScoreListViewSet.as_view(), name='scores-api'),
    path('api/rankings/', RankingsViewSet.as_view(), name='rankings-api'),
    path('api/public-images/', PublicImageViewSet.as_view(), name='public-images-api'),
    path('api/request-reset-account/', ResetPasswordViewSet.as_view(), name='request-reset-account-api'),
    path('api/search', SearchView.as_view(), name='search-api'),
    path('api/meanings/<int:pk>', MeaningView.as_view(), name='meaning-api'),
    path('api/words/<int:pk>', WordView.as_view(), name='word-api')
]
