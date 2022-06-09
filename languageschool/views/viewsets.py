from languageschool.models import Article, Category, Conjugation, Language, Meaning, Score, Word
from languageschool.serializer import ArticleSerializer, CategorySerializer, ConjugationSerializer, LanguageSerializer, ListScoreSerializer, MeaningSerializer, ScoreSerializer, WordSerializer
from rest_framework import generics, views, status
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

class ScoreViewSet(views.APIView):
    '''
    GET requests: we can optionally specify two URL parameters "language_id" and "game" in order to search a score of the authenticated
    user for a game in the specified language. If any of these two parameters is not specified, all the scores are returned.

    POST requests: creates a score record with default score of 1. The JSON with the corresponding language and game must be specified 
    as follows: 

        {
            "language": <language_name>,
            "game": <game_name>
        }

    POST requests: updates a score record by incrementing the score. The JSON with the corresponding language and game must be specified 
    as follows: 

        {
            "language": <language_name>,
            "game": <game_name>
        }
    '''
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.GET.get("language_id") and request.GET.get("game"):
            scores = Score.objects.filter(user = request.user, language = request.GET.get("language_id"), game = request.GET.get("game"))
        else:
            scores = Score.objects.all()
        serializer = ListScoreSerializer(scores, many=True)
        return Response(serializer.data)
            
    def post(self, request):
        data = request.data
        serializer = ScoreSerializer(data = data, context = {"user": request.user})
        scores = Score.objects.filter(user = request.user, language__language_name = data.get("language"), game = data.get("game"))
        if serializer.is_valid(raise_exception = True) and len(scores) == 0:
            serializer.save()
            return Response({"success" : "Score created"}, status=status.HTTP_201_CREATED)
        return Response({"error" : "The specified score already exists. Please, perform an UPDATE(PUT request) if you want to increment it."}, status=status.HTTP_409_CONFLICT)

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
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error" : "The specified score was not found. Please, perform a create(POST request) in order to create it."}, status=status.HTTP_409_CONFLICT)
    