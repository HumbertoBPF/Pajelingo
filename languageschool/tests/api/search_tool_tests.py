import math
import random
import string
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Word
from languageschool.tests.utils import get_user_token, get_alphabetically_ordered_url

BASE_URL = reverse("search-api")


def assert_word_returned_in_payload(result, user=None):
    word = Word.objects.get(id=result.get("id"))
    assert word.language.language_name == result.get("language")
    assert word.word_name == result.get("word_name")
    assert word.article_id == result.get("article")
    if user is not None:
        assert user.favorite_words.contains(word) is result.get("is_favorite")


@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_search_without_filters(api_client, account, words, languages, is_authenticated):
    """
    Checks that the endpoint returns all the words properly paginated when no filter is specified.
    """
    user, password = account()[0]

    query_params = {}

    for language in languages.order_by("language_name"):
        query_params[language.language_name] = "true"

    url = get_alphabetically_ordered_url(BASE_URL, query_params)
    next_page = "http://testserver{}".format(url)
    expected_previous_page = None
    expected_number_results = words.count()

    number_pages = 0

    while next_page is not None:
        if is_authenticated:
            token = get_user_token(api_client, user, password)
            response = api_client.get(next_page, HTTP_AUTHORIZATION="Token {}".format(token))
        else:
            response = api_client.get(next_page)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == expected_number_results
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert_word_returned_in_payload(result, user if is_authenticated else None)

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(expected_number_results/12)


@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_search_with_language_filter(api_client, account, words, languages, is_authenticated):
    """
    Checks that the endpoint returns only the words in the selected language properly paginated when the language
    filter is specified.
    """
    user, password = account()[0]

    random_language = random.choice(languages)

    query_string = urlencode({
        random_language.language_name: "true"
    })
    next_page = "http://testserver{}?{}".format(BASE_URL, query_string)
    expected_previous_page = None
    expected_number_results = words.filter(language=random_language).count()

    number_pages = 0

    while next_page is not None:
        if is_authenticated:
            token = get_user_token(api_client, user, password)
            response = api_client.get(next_page, HTTP_AUTHORIZATION="Token {}".format(token))
        else:
            response = api_client.get(next_page)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == expected_number_results
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert result.get("language") == random_language.language_name
            assert_word_returned_in_payload(result, user if is_authenticated else None)

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(expected_number_results/12)


@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_search_with_search_filter(api_client, account, words, languages, is_authenticated):
    """
    Checks that the endpoint returns only the words that contain the specified search pattern when the search
    filter is specified.
    """
    user, password = account()[0]

    search_filter = get_random_string(1, string.ascii_letters)

    query_params = {
        "search": search_filter
    }

    for language in languages.order_by("language_name"):
        query_params[language.language_name] = "true"

    url = get_alphabetically_ordered_url(BASE_URL, query_params)
    next_page = "http://testserver{}".format(url)
    expected_previous_page = None
    expected_number_results = words.filter(word_name__icontains=search_filter).count()

    number_pages = 0

    while next_page is not None:
        if is_authenticated:
            token = get_user_token(api_client, user, password)
            response = api_client.get(next_page, HTTP_AUTHORIZATION="Token {}".format(token))
        else:
            response = api_client.get(next_page)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == expected_number_results
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert search_filter.lower() in result.get("word_name").lower()
            assert_word_returned_in_payload(result, user if is_authenticated else None)

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(expected_number_results/12)
