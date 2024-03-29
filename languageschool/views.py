import base64

from django.db.models import Sum
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import views, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from languageschool.models import Language, Word, Meaning, Conjugation, Game, Category, Article, Score, User
from languageschool.paginators import SearchPaginator, RankingsPaginator, SearchAccountPaginator
from languageschool.permissions import AllowPostOnly
from languageschool.serializers import WordSerializer, MeaningSerializer, ArticleGameAnswerSerializer, \
    VocabularyGameAnswerSerializer, ConjugationGameAnswerSerializer, ProfilePictureSerializer, ResetAccountSerializer, \
    GameSerializer, LanguageSerializer, CategorySerializer, ArticleSerializer, ConjugationSerializer, \
    RankingsSerializer, ListScoreSerializer, UserSerializer, RequestResetAccountSerializer, FavoriteWordsSerializer, \
    ArticleGameSetupSerializer, ConjugationGameSetupSerializer, VocabularyGameSetupSerializer, AccountSerializer
from languageschool.utils import send_activation_account_email
from pajelingo import settings
from pajelingo.tokens import account_activation_token

MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE = "You must specify a language and a game"


class GameViewSet(generics.ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        return Game.objects.all()


class LanguageViewSet(generics.ListAPIView):
    serializer_class = LanguageSerializer

    def get_queryset(self):
        return Language.objects.all()


class CategoryViewSet(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()


class ArticleViewSet(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.all()


class WordViewSet(generics.ListAPIView):
    serializer_class = WordSerializer
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Word.objects.all()


class MeaningViewSet(generics.ListAPIView):
    serializer_class = MeaningSerializer

    def get_queryset(self):
        return Meaning.objects.all()


class ConjugationViewSet(generics.ListAPIView):
    serializer_class = ConjugationSerializer

    def get_queryset(self):
        return Conjugation.objects.all()


class RankingsViewSet(generics.ListAPIView):
    pagination_class = RankingsPaginator
    serializer_class = RankingsSerializer

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)

        username = self.request.query_params.get('user')
        user = get_object_or_404(User, username=username) if (username is not None) else None

        scores = self.get_queryset()

        user_score = None

        for score in scores:
            if (user is not None) and (score["user__username"] == user.username):
                user_score = {
                    "position": score["position"],
                    "user": score["user__username"],
                    "score": score["score"]
                }
                break

        return Response({**response.data, "user_score": user_score})

    def get_queryset(self):
        language_name = self.request.query_params.get('language')
        language = get_object_or_404(Language, language_name=language_name)

        scores = Score.objects.filter(language=language).values('user__username')\
            .annotate(score=Sum('score')).order_by('-score')

        i = 1

        for score in scores:
            score["position"] = i
            i += 1

        return scores


class ScoreListViewSet(generics.ListAPIView):
    serializer_class = ListScoreSerializer

    def get_queryset(self):
        queryset = Score.objects.all()

        language = self.request.query_params.get('language')
        user = self.request.query_params.get('user')

        if language is not None:
            queryset = queryset.filter(language__language_name=language)

        if user is not None:
            queryset = queryset.filter(user__username=user)

        return queryset


class UserViewSet(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowPostOnly]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()

        send_activation_account_email(new_user)

        serializer = UserSerializer(new_user)

        return Response(serializer.data, status.HTTP_201_CREATED)

    def put(self, request):
        serializer = UserSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()

        serializer = UserSerializer(updated_user)

        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScoreViewSet(views.APIView):
    """
    GET requests: we can optionally specify two URL parameters "language" and "game" in order to search a score of the authenticated
    user for a game in the specified language. If any of these two parameters is not specified, all the scores are returned.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        language = request.GET.get("language")
        game = request.GET.get("game")

        if (language is None) or (game is None):
            return Response({"error": MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        scores = Score.objects.filter(user=request.user, language__language_name=language, game__id=game)
        serializer = ListScoreSerializer(scores, many=True)
        return Response(serializer.data)


class PublicImageViewSet(views.APIView):
    def get(self, request):
        resource = request.GET.get("url")

        if resource is None:
            return Response({
                "error": "The resource requested is null"
            }, status.HTTP_400_BAD_REQUEST)

        if resource.startswith("/media/images/models/AppUser/"):
            raise PermissionDenied()

        url = settings.MEDIA_ROOT.replace("\\", "/").split("/media")[0] + resource

        try:
            with open(url, "rb") as img:
                converted_string = base64.b64encode(img.read())
        except FileNotFoundError:
            return Response({
                "error": "The requested image does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "image": converted_string
        }, status=status.HTTP_200_OK)


class RequestResetPasswordView(views.APIView):
    def post(self, request):
        serializer = RequestResetAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    pagination_class = SearchPaginator
    serializer_class = WordSerializer

    def get_queryset(self):
        search_pattern = self.request.query_params.get("search", "")
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
    authentication_classes = [TokenAuthentication]

    def get(self, request, pk):
        word = get_object_or_404(Word, pk=pk)
        serializer = WordSerializer(word, context={"request": request})

        word_image = None
        if word.image:
            img = word.image.open("rb")
            word_image = base64.b64encode(img.read())

        return Response(data={**serializer.data, "image": word_image}, status=status.HTTP_200_OK)


class ArticleGameView(views.APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        serializer = ArticleGameSetupSerializer(data=request.GET, context={"request": request})
        serializer.is_valid(raise_exception=True)

        word = serializer.save()

        return Response(data={
            "id": word.id,
            "word": word.word_name
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ArticleGameAnswerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        response_data = serializer.save()

        return Response(data=response_data, status=status.HTTP_200_OK)


class VocabularyGameView(views.APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        serializer = VocabularyGameSetupSerializer(data=request.GET, context={"request": request})
        serializer.is_valid(raise_exception=True)

        word = serializer.save()

        return Response(data={
            "id": word.id,
            "word": word.word_name
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = VocabularyGameAnswerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        response_data = serializer.save()

        return Response(data=response_data, status=status.HTTP_200_OK)


class ConjugationGameView(views.APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        serializer = ConjugationGameSetupSerializer(data=request.GET, context={"request": request})
        serializer.is_valid(raise_exception=True)

        conjugation = serializer.save()

        return Response(data={
            "id": conjugation.word_id,
            "word": conjugation.word.word_name,
            "tense": conjugation.tense
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ConjugationGameAnswerSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        response_data = serializer.save()

        return Response(data=response_data, status=status.HTTP_200_OK)


class ActivationView(views.APIView):
    def put(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if user.is_active or (not account_activation_token.check_token(user, token)):
                raise PermissionDenied()
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise PermissionDenied()

        user.is_active = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfilePictureView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ProfilePictureSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetAccountView(views.APIView):
    def put(self, request, uidb64, token):
        try:
            pk = force_str(urlsafe_base64_decode(uidb64))
        except(TypeError, ValueError, OverflowError):
            raise PermissionDenied()

        serializer = ResetAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(pk=pk, token=token)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteWordsListView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = SearchPaginator
    serializer_class = WordSerializer

    def get_queryset(self):
        search_pattern = self.request.query_params.get("search", "")
        languages = []
        for language in Language.objects.all():
            if self.request.query_params.get(language.language_name) == "true":
                languages.append(language)
        return self.request.user.favorite_words\
            .filter(word_name__icontains=search_pattern, language__in=languages).order_by(Lower('word_name'))


class FavoriteWordsView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        serializer = FavoriteWordsSerializer(data=request.data, context={
            "word_id": pk,
            "user": request.user
        })
        serializer.is_valid(raise_exception=True)
        word = serializer.save()

        serializer = WordSerializer(word, context={
            "request": request
        })
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AccountsView(generics.ListAPIView):
    pagination_class = SearchAccountPaginator
    serializer_class = AccountSerializer

    def get_queryset(self):
        search_pattern = self.request.query_params.get("q", "")

        return User.objects.filter(username__icontains=search_pattern).order_by("username")


class AccountView(views.APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = AccountSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
