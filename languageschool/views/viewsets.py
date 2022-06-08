from django.http import Http404
from languageschool import serializer
from languageschool.models import Article, Category, Conjugation, Language, Meaning, Score, Word
from languageschool.serializer import ArticleSerializer, CategorySerializer, ConjugationSerializer, LanguageSerializer, MeaningSerializer, ScoreSerializer, WordSerializer, ScoreModelSerializer
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated


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

class ScoreViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Score.objects.all()
        return queryset
    serializer_class = ScoreModelSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

class NewScoreViewSet(views.APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ScoreSerializer(data = request.data, context = {"user": request.user})
        if serializer.is_valid(raise_exception = True):
            score = serializer.save()
        return Response({"success" : "Score created"})

class IncrementalScoreViewSet(views.APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        # Get request data
        data = request.data
        # Localize the specified score
        scores = Score.objects.filter(user = request.user, language__language_name = data.get("language"), game = data.get("game"))
        # If some score was found
        if len(scores) > 0:
            score = scores[0]
            # Try to update the score
            serializer = ScoreSerializer(instance=score, data=data, partial=True)
            if serializer.is_valid(raise_exception = True):
                score = serializer.save()
        else:
            raise Http404()
        return Response({"successs": "Score updated"})