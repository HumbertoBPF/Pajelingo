from django.contrib import admin

from languageschool.models import Article, Category, Conjugation, Language, Meaning, Word

class LanguageDisplay(admin.ModelAdmin):
    list_display = ('id','language_name')
    list_display_links = ('id','language_name')
    list_per_page = 10

class CategoryDisplay(admin.ModelAdmin):
    list_display = ('id','category_name')
    list_display_links = ('id','category_name')
    search_fields = ('category_name',)
    list_per_page = 10

class ArticleDisplay(admin.ModelAdmin):
    list_display = ('id','article_name','language')
    list_display_links = ('id','article_name')
    list_per_page = 10

class WordDisplay(admin.ModelAdmin):
    list_display = ('id','word_name','language','article')
    list_display_links = ('id','word_name')
    search_fields = ('word_name',)
    list_filter = ('language','category')
    list_per_page = 10

class ConjugationDisplay(admin.ModelAdmin):
    list_display = ('id','word','tense','conjugation_1','conjugation_2','conjugation_3','conjugation_4','conjugation_5','conjugation_6')
    list_display_links = ('id','word')
    list_per_page = 10

# Register your models here.
admin.site.register(Language,LanguageDisplay)
admin.site.register(Category,CategoryDisplay)
admin.site.register(Article,ArticleDisplay)
admin.site.register(Word,WordDisplay)
admin.site.register(Meaning)
admin.site.register(Conjugation,ConjugationDisplay)