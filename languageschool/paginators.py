from rest_framework.pagination import PageNumberPagination


class RankingsPaginator(PageNumberPagination):
    page_size = 10