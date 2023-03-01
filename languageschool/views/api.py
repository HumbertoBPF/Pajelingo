import base64

from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from rest_framework import views, generics, status
from rest_framework.response import Response

from languageschool.models import Language, Word, Meaning
from languageschool.paginators import SearchPaginator
from languageschool.serializers import WordSerializer, MeaningSerializer


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
