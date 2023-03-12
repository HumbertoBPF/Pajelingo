import base64
import random

from django.contrib.auth.models import User
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import views, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from languageschool.models import Language, Word, Meaning, Conjugation, AppUser
from languageschool.paginators import SearchPaginator
from languageschool.serializers import WordSerializer, MeaningSerializer, ArticleGameAnswerSerializer, \
    VocabularyGameAnswerSerializer, ConjugationGameAnswerSerializer, ProfilePictureSerializer, ResetAccountSerializer
from pajelingo.tokens import account_activation_token


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
    authentication_classes = [TokenAuthentication]

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
        serializer = ArticleGameAnswerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        is_answer_correct, correct_answer, score = serializer.save()

        return Response(data={
            "result": is_answer_correct,
            "correct_answer": correct_answer,
            "score": score
        }, status=status.HTTP_200_OK)


class VocabularyGameView(views.APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        language_name = request.GET.get("language")

        target_language = get_object_or_404(Language, language_name=language_name)

        selected_word = random.choice(Word.objects.filter(language=target_language))

        return Response(data={
            "id": selected_word.id,
            "word": selected_word.word_name
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = VocabularyGameAnswerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        is_answer_correct, correct_answer, score = serializer.save()

        return Response(data={
            "result": is_answer_correct,
            "correct_answer": correct_answer,
            "score": score
        }, status=status.HTTP_200_OK)


class ConjugationGameView(views.APIView):
    authentication_classes = [TokenAuthentication]

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
        serializer = ConjugationGameAnswerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        is_answer_correct, correct_answer, score = serializer.save()

        return Response(data={
            "result": is_answer_correct,
            "correct_answer": correct_answer,
            "score": score
        }, status=status.HTTP_200_OK)


class ActivationView(views.APIView):
    def put(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.filter(pk=uid, is_active=False).first()
        except(TypeError, ValueError, OverflowError):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ProfilePictureView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        app_user = AppUser.objects.filter(user=request.user).first()
        serializer = ProfilePictureSerializer(app_user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetAccountView(views.APIView):
    def put(self, request, uidb64, token):
        try:
            pk = force_str(urlsafe_base64_decode(uidb64))
        except(TypeError, ValueError, OverflowError):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ResetAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.save(pk=pk, token=token):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_403_FORBIDDEN)
