import base64
import random

from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from rest_framework import views, generics, status
from rest_framework.response import Response

from languageschool.models import Language, Word, Meaning, Conjugation
from languageschool.paginators import SearchPaginator
from languageschool.serializers import WordSerializer, MeaningSerializer, ArticleGameAnswerSerializer, \
    VocabularyGameAnswerSerializer, ConjugationGameAnswerSerializer


class SearchView(generics.ListAPIView):
    pagination_class = SearchPaginator
    serializer_class = WordSerializer

    def get_queryset(self):
        search_pattern = self.request.query_params.get("search")
        languages = []
        for language in Language.objects.all():
            if self.request.query_params.get(language.language_name) == "true":
                languages.append(language)
        # Results containing the specified string
        return Word.objects \
            .filter(word_name__icontains=search_pattern, language__in=languages).order_by(Lower('word_name'))


class MeaningView(views.APIView):
    def get(self, request, pk):
        word = get_object_or_404(Word, pk=pk)
        meanings = Meaning.objects.filter(word=word)
        serializer = MeaningSerializer(meanings, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class WordView(views.APIView):
    def get(self, request, pk):
        word = get_object_or_404(Word, pk=pk)
        serializer = WordSerializer(word)

        word_image = None
        if word.image:
            img = word.image.open("rb")
            word_image = base64.b64encode(img.read())

        return Response(data={**serializer.data, "image": word_image}, status=status.HTTP_200_OK)


class ArticleGameView(views.APIView):
    def get(self, request):
        language_name = request.GET.get("language")

        if language_name == "English":
            return Response({"error": "Invalid language"},status=status.HTTP_400_BAD_REQUEST)

        language = get_object_or_404(Language, language_name=language_name)

        word = random.choice(Word.objects.filter(language=language).exclude(article=None))

        return Response(data={
            "id": word.id,
            "word": word.word_name
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ArticleGameAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_answer_correct, correct_answer = serializer.save()

        return Response(data={
            "result": is_answer_correct,
            "correct_answer": correct_answer
        }, status=status.HTTP_200_OK)


class VocabularyGameView(views.APIView):
    def get(self, request):
        language_name = request.GET.get("language")

        target_language = get_object_or_404(Language, language_name=language_name)

        selected_word = random.choice(Word.objects.filter(language=target_language))

        return Response(data={
            "id": selected_word.id,
            "word": selected_word.word_name
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = VocabularyGameAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_answer_correct, correct_answer = serializer.save()

        return Response(data={
            "result": is_answer_correct,
            "correct_answer": correct_answer
        }, status=status.HTTP_200_OK)


class ConjugationGameView(views.APIView):
    def get(self, request):
        language_name = request.GET.get("language")

        language = get_object_or_404(Language, language_name=language_name)

        verb = random.choice(Word.objects.filter(language=language).filter(category__category_name="verbs"))
        conjugation = random.choice(Conjugation.objects.filter(word=verb.id))

        return Response(data={
            "id": verb.id,
            "word": verb.word_name,
            "tense": conjugation.tense
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ConjugationGameAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_answer_correct, correct_answer = serializer.save()

        return Response(data={
            "result": is_answer_correct,
            "correct_answer": correct_answer
        }, status=status.HTTP_200_OK)
