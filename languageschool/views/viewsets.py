from django.shortcuts import get_object_or_404
from rest_framework import generics, views, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from languageschool.models import Article, Category, Conjugation, Game, Language, Meaning, Score, Word
from languageschool.permissions import AllowPostOnly
from languageschool.serializer import ArticleSerializer, CategorySerializer, ConjugationSerializer, GameSerializer, \
    LanguageSerializer, ListScoreSerializer, MeaningSerializer, ScoreSerializer, WordSerializer, UserSerializer

MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE = "You must specify a language and a game"
CONFLICT_SCORE_MESSAGE = "The specified score already exists. Please, perform an UPDATE(PUT request) if you want to increment it."


class GameViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Game.objects.all()
        return queryset

    serializer_class = GameSerializer


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


class ScoreListViewSet(generics.ListAPIView):
    def get_queryset(self):
        queryset = Score.objects.all()
        return queryset

    serializer_class = ListScoreSerializer


class UserViewSet(views.APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowPostOnly]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email
         }, status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response({
            "username": serializer.data.get("username"),
            "email": serializer.data.get("email")
         }, status.HTTP_201_CREATED)

    def put(self, request):
        serializer = UserSerializer(instance=request.user, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response({
            "username": serializer.data.get("username"),
            "email": serializer.data.get("email")
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
