import math
import random
import string
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Word

BASE_URL = reverse("search-api")


def get_alphabetically_ordered_url(query_params):
    keys = list(query_params.keys())

    if len(keys) == 0:
        return BASE_URL

    keys.sort()
    url = "{}?{}={}".format(BASE_URL, keys[0], query_params.get(keys[0]))

    for i in range(1, len(keys)):
        key = keys[i]
        url = "{}&{}={}".format(url, key, query_params.get(key))

    return url


@pytest.mark.django_db
def test_search_without_filters(api_client, words, languages):
    """
    Checks that the endpoint returns all the words properly paginated when no filter is specified.
    """
    query_params = {}

    for language in languages.order_by("language_name"):
        query_params[language.language_name] = "true"

    url = get_alphabetically_ordered_url(query_params)
    next_page = "http://testserver{}".format(url)
    expected_previous_page = None

    number_pages = 0

    while next_page is not None:
        print(next_page)
        response = api_client.get(next_page)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == len(words)
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert Word.objects.filter(id=result.get("id"),
                                       language__language_name=result.get("language"),
                                       category__category_name=result.get("category"),
                                       word_name=result.get("word_name"),
                                       article__id=result.get("article")).exists()

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(len(words)/12)


@pytest.mark.django_db
def test_search_with_language_filter(api_client, words, languages):
    """
    Checks that the endpoint returns only the words in the selected language properly paginated when the language
    filter is specified.
    """
    random_language = random.choice(languages)
    matched_words = words.filter(language=random_language)

    query_string = urlencode({
        random_language.language_name: "true"
    })
    next_page = "http://testserver{}?{}".format(BASE_URL, query_string)
    expected_previous_page = None

    number_pages = 0

    while next_page is not None:
        response = api_client.get(next_page)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == len(matched_words)
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert result.get("language") == random_language.language_name
            assert Word.objects.filter(id=result.get("id"),
                                       language__language_name=result.get("language"),
                                       category__category_name=result.get("category"),
                                       word_name=result.get("word_name"),
                                       article__id=result.get("article")).exists()

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(len(matched_words)/12)


@pytest.mark.django_db
def test_search_with_search_filter(api_client, words, languages):
    """
    Checks that the endpoint returns only the words that contain the specified search pattern when the search
    filter is specified.
    """
    search_filter = get_random_string(1, string.ascii_letters)
    matched_words = words.filter(word_name__icontains=search_filter)

    query_params = {
        "search": search_filter
    }

    for language in languages.order_by("language_name"):
        query_params[language.language_name] = "true"

    url = get_alphabetically_ordered_url(query_params)
    next_page = "http://testserver{}".format(url)
    expected_previous_page = None

    number_pages = 0

    while next_page is not None:
        response = api_client.get(next_page)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == len(matched_words)
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert search_filter.lower() in result.get("word_name").lower()
            assert Word.objects.filter(id=result.get("id"),
                                       language__language_name=result.get("language"),
                                       category__category_name=result.get("category"),
                                       word_name=result.get("word_name"),
                                       article__id=result.get("article")).exists()

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(len(matched_words)/12)
