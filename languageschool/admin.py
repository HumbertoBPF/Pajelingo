from django.contrib import admin

from languageschool.models import AppUser, Article, Category, Conjugation, Game, Language, Meaning, Score, Word


class LanguageDisplay(admin.ModelAdmin):
    list_display = ('id', 'language_name')
    list_display_links = ('id', 'language_name')
    search_fields = ('language_name',)
    list_per_page = 10


class CategoryDisplay(admin.ModelAdmin):
    list_display = ('id', 'category_name')
    list_display_links = ('id', 'category_name')
    search_fields = ('category_name',)
    list_per_page = 10


class ArticleDisplay(admin.ModelAdmin):
    list_display = ('id', 'article_name', 'language')
    list_display_links = ('id', 'article_name')
    search_fields = ('article_name',)
    list_filter = ('language',)
    list_per_page = 10


class WordDisplay(admin.ModelAdmin):
    list_display = ('id', 'word_name', 'language', 'article')
    list_display_links = ('id', 'word_name')
    search_fields = ('word_name',)
    list_filter = ('language', 'category')
    list_per_page = 10
    autocomplete_fields = ['synonyms']


class ConjugationDisplay(admin.ModelAdmin):
    list_display = ('id', 'word', 'tense', 'conjugation_1', 'conjugation_2', 'conjugation_3', 'conjugation_4', 'conjugation_5', 'conjugation_6')
    list_display_links = ('id', 'word')
    search_fields = ('word__word_name',)
    list_filter = ('tense',)
    list_per_page = 10


class MeaningDisplay(admin.ModelAdmin):
    list_display = ('id', 'word', 'meaning')
    list_display_links = ('id', 'word')
    search_fields = ('word__word_name',)
    list_per_page = 10


class ScoreDisplay(admin.ModelAdmin):
    list_display = ('id', 'user', 'language', 'game', 'score')
    list_display_links = ('id',)
    search_fields = ('user__username',)
    list_filter = ('language', 'game')
    list_per_page = 10


class AppUserDisplay(admin.ModelAdmin):
    list_display = ('id', 'user')
    list_display_links = ('id', 'user')
    search_fields = ('user__username',)
    list_per_page = 10


class GameDisplay(admin.ModelAdmin):
    list_display = ('id', 'android_game_activity', 'game_name')
    list_display_links = ('id', 'android_game_activity', 'game_name')
    search_fields = ('game_name', 'android_game_activity')
    list_per_page = 10


# Register your models here.
admin.site.register(Language, LanguageDisplay)
admin.site.register(Category, CategoryDisplay)
admin.site.register(Article, ArticleDisplay)
admin.site.register(Word, WordDisplay)
admin.site.register(Meaning, MeaningDisplay)
admin.site.register(Conjugation, ConjugationDisplay)
admin.site.register(Score, ScoreDisplay)
admin.site.register(AppUser, AppUserDisplay)
admin.site.register(Game, GameDisplay)
