from languageschool import serializer
from languageschool.models import Article, Category, Conjugation, Language, Meaning, Word
from languageschool.serializer import ArticleSerializer, CategorySerializer, ConjugationSerializer, LanguageSerializer, MeaningSerializer, WordSerializer
from rest_framework import generics

class LanguageViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Language.objects.all()
        return queryset
    serializer_class = LanguageSerializer

class CategoryViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset
    serializer_class = CategorySerializer

class ArticleViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Article.objects.all()
        return queryset
    serializer_class = ArticleSerializer

class WordViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Word.objects.all()
        return queryset
    serializer_class = WordSerializer

class MeaningViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Meaning.objects.all()
        return queryset
    serializer_class = MeaningSerializer

class ConjugationViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Conjugation.objects.all()
        return queryset
    serializer_class = ConjugationSerializer