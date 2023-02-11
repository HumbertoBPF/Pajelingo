import base64

from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import generics, views, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from languageschool.models import Article, Category, Conjugation, Game, Language, Meaning, Score, Word, AppUser
from languageschool.paginators import RankingsPaginator
from languageschool.permissions import AllowPostOnly
from languageschool.serializers import ArticleSerializer, CategorySerializer, ConjugationSerializer, GameSerializer, \
    LanguageSerializer, ListScoreSerializer, MeaningSerializer, ScoreSerializer, WordSerializer, UserSerializer, \
    RankingsSerializer
from languageschool.utils import send_activation_account_email, send_reset_account_email
from pajelingo import settings

MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE = "You must specify a language and a game"
CONFLICT_SCORE_MESSAGE = "The specified score already exists. Please, perform an UPDATE(PUT request) if you want to increment it."


class GameViewSet(generics.ListAPIView):
    def get_queryset(self):
        return Game.objects.all()

    serializer_class = GameSerializer


class LanguageViewSet(generics.ListAPIView):
    def get_queryset(self):
        return Language.objects.all()

    serializer_class = LanguageSerializer


class CategoryViewSet(generics.ListAPIView):
    def get_queryset(self):
        return Category.objects.all()

    serializer_class = CategorySerializer


class ArticleViewSet(generics.ListAPIView):
    def get_queryset(self):
        return Article.objects.all()

    serializer_class = ArticleSerializer


class WordViewSet(generics.ListAPIView):
    def get_queryset(self):
        return Word.objects.all()

    serializer_class = WordSerializer


class MeaningViewSet(generics.ListAPIView):
    def get_queryset(self):
        return Meaning.objects.all()

    serializer_class = MeaningSerializer


class ConjugationViewSet(generics.ListAPIView):
    def get_queryset(self):
        return Conjugation.objects.all()

    serializer_class = ConjugationSerializer


class RankingsViewSet(generics.ListAPIView):
    pagination_class = RankingsPaginator

    def get_queryset(self):
        username = self.request.query_params.get('user')
        user = get_object_or_404(User, username=username) if (username is not None) else None

        language_name = self.request.query_params.get('language')
        language = get_object_or_404(Language, language_name=language_name)

        scores = Score.objects.filter(language=language).values('user__username')\
            .annotate(score=Sum('score')).order_by('-score')

        i = 1

        for score in scores:
            score["position"] = i

            if (user is not None) and (score["user__username"] == user.username):
                return [score]

            i += 1

        return scores

    serializer_class = RankingsSerializer


class ScoreListViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Score.objects.all()

        language = self.request.query_params.get('language')
        user = self.request.query_params.get('user')

        if language is not None:
            queryset = queryset.filter(language__language_name=language)

        if user is not None:
            queryset = queryset.filter(user__username=user)

        return queryset

    serializer_class = ListScoreSerializer


class UserViewSet(views.APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowPostOnly]

    def get_profile_picture(self, app_user):
        if app_user.picture:
            try:
                img = app_user.picture.open("rb")
                return base64.b64encode(img.read())
            except FileNotFoundError as e:
                print(e)

    def get(self, request):
        app_user = AppUser.objects.filter(user__id=request.user.id).first()

        return Response({
            "username": app_user.user.username,
            "email": app_user.user.email,
            "picture": self.get_profile_picture(app_user)
        }, status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            new_user = serializer.save()

            send_activation_account_email(request, new_user)

            app_user = AppUser.objects.filter(user__id=new_user.id).first()

            return Response({
                "username": app_user.user.username,
                "email": app_user.user.email,
                "picture": self.get_profile_picture(app_user)
            }, status.HTTP_201_CREATED)

    def put(self, request):
        serializer = UserSerializer(instance=request.user, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        app_user = AppUser.objects.filter(user__id=request.user.id).first()

        return Response({
            "username": app_user.user.username,
            "email": app_user.user.email,
            "picture": self.get_profile_picture(app_user)
        }, status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScoreViewSet(views.APIView):
    """
    GET requests: we can optionally specify two URL parameters "language" and "game" in order to search a score of the authenticated
    user for a game in the specified language. If any of these two parameters is not specified, all the scores are returned.

    POST requests: creates a score record with default score of 1. The JSON with the corresponding language and game must be specified
    as follows:

        {
            "language": <language_name>,
            "game": <id>
        }

    A JSON representation of the created score is returned.

    PUT requests: increments an existing score record with 1. The score record is specified in the request with its game and language.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        language = request.GET.get("language")
        game = request.GET.get("game")

        if (language is None) or (game is None):
            return Response({"error": MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        scores = Score.objects.filter(user=request.user, language__language_name=language, game__id=game)
        serializer = ListScoreSerializer(scores, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        serializer = ScoreSerializer(data=data, context={"user": request.user})
        scores = Score.objects.filter(user=request.user, language__language_name=data.get("language"),
                                      game__id=data.get("game"))
        if serializer.is_valid(raise_exception=True) and len(scores) == 0:
            score = serializer.save()
            serializer = ListScoreSerializer(score)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": CONFLICT_SCORE_MESSAGE}, status=status.HTTP_409_CONFLICT)

    def put(self, request, score_id=None):
        # Localize the specified score
        score = get_object_or_404(Score, id=score_id)
        # Checks if the logged user can update it
        if request.user != score.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            # Try to update the score
        serializer = ScoreSerializer(instance=score, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            score = serializer.save()
            serializer = ListScoreSerializer(score)
            return Response(serializer.data)


class PublicImageViewSet(views.APIView):
    def get(self, request):
        resource = request.GET.get("url")

        if resource is None:
            return Response({
                "error": "The resource requested is null"
            }, status.HTTP_400_BAD_REQUEST)

        app_user = AppUser()
        if resource.startswith("/media/images/models/{}/".format(app_user.__class__.__name__)):
            return Response({
                "error": "This picture is private"
            }, status.HTTP_403_FORBIDDEN)

        url = settings.MEDIA_ROOT.replace("\\", "/").split("/media")[0] + resource

        try:
            with open(url, "rb") as img:
                converted_string = base64.b64encode(img.read())
        except FileNotFoundError:
            return Response({
                "error": "The requested image does not exist"
            }, status.HTTP_404_NOT_FOUND)

        return Response({
            "image": converted_string
        }, status.HTTP_200_OK)


class ResetPasswordViewSet(views.APIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email, is_active=True).first()

        if user is not None:
            send_reset_account_email(request, user)

        return Response(status.HTTP_200_OK)
