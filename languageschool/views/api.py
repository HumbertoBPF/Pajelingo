from django.db.models.functions import Lower
from rest_framework import views, generics

from languageschool.models import Language, Word
from languageschool.paginators import SearchPaginator
from languageschool.serializers import WordSerializer


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

