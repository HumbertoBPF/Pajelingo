import math
import random
import string
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.tests.utils import get_user_token, get_alphabetically_ordered_url

URL_GET = reverse("list-favorite-words-api")


def assert_word(returned_word, expected_word):
    assert expected_word.id == returned_word.get("id")
    assert expected_word.word_name == returned_word.get("word_name")
    assert expected_word.language.language_name == returned_word.get("language")
    assert expected_word.article.id == returned_word.get("article")
    expected_category = None if (expected_word.category is None) else expected_word.category.category_name
    assert expected_category == returned_word.get("category")
    assert list(expected_word.synonyms.all().values_list('id', flat=True)) == returned_word.get("synonyms")
    expected_image_url = expected_word.image.url if expected_word.image else None
    assert expected_image_url == returned_word.get("image")


@pytest.mark.django_db
def test_favorite_words_put_requires_token_authentication(api_client, words):
    random_word = random.choice(words)
    url_put = reverse("favorite-words-api", kwargs={"pk": random_word.id})

    response = api_client.put(url_put)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_favorite_words_put_require_is_favorite_parameter(api_client, account, words):
    user, password = account()[0]
    token = get_user_token(api_client, user, password)

    random_word = random.choice(words)
    url_put = reverse("favorite-words-api", kwargs={"pk": random_word.id})

    response = api_client.put(url_put, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_favorite_words_put_add_favorite_word(api_client, account, words):
    user, password = account()[0]
    token = get_user_token(api_client, user, password)

    random_word = random.choice(words)
    url_put = reverse("favorite-words-api", kwargs={"pk": random_word.id})

    response = api_client.put(url_put, data={
        "is_favorite": True
    }, HTTP_AUTHORIZATION="Token {}".format(token))
    
    returned_word = response.data

    assert response.status_code == status.HTTP_200_OK
    assert random_word in user.favorite_words.all()
    assert_word(returned_word, random_word)
    assert returned_word.get("is_favorite")


@pytest.mark.django_db
def test_favorite_words_put_remove_favorite_word(api_client, account, words):
    user, password = account()[0]
    token = get_user_token(api_client, user, password)

    random_word = random.choice(user.favorite_words.all())
    url_put = reverse("favorite-words-api", kwargs={"pk": random_word.id})

    response = api_client.put(url_put, data={
        "is_favorite": False
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    returned_word = response.data

    assert response.status_code == status.HTTP_200_OK
    assert_word(returned_word, random_word)
    assert not returned_word.get("is_favorite")


@pytest.mark.django_db
def test_favorite_words_get_requires_token_authentication(api_client, words):
    response = api_client.get(URL_GET)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_favorite_words_get_without_filters(api_client, account, languages):
    """
    Checks that the endpoint returns all the favorite words properly paginated when no filter is specified.
    """
    user, password = account()[0]
    favorite_words = user.favorite_words.all()
    token = get_user_token(api_client, user, password)

    query_params = {}

    for language in languages.order_by("language_name"):
        query_params[language.language_name] = "true"

    url = get_alphabetically_ordered_url(URL_GET, query_params)
    next_page = "http://testserver{}".format(url)
    expected_previous_page = None

    number_pages = 0

    while next_page is not None:
        response = api_client.get(next_page, HTTP_AUTHORIZATION="Token {}".format(token))

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == len(favorite_words)
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert favorite_words.filter(id=result.get("id"),
                                        language__language_name=result.get("language"),
                                        category__category_name=result.get("category"),
                                        word_name=result.get("word_name"),
                                        article__id=result.get("article")).exists()
            assert result.get("is_favorite")

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(len(favorite_words)/12)


@pytest.mark.django_db
def test_favorite_words_get_with_language_filter(api_client, account, languages):
    """
    Checks that the endpoint returns only the favorite words in the selected language properly paginated when the
    language filter is specified.
    """
    user, password = account()[0]
    favorite_words = user.favorite_words.all()
    token = get_user_token(api_client, user, password)

    random_language = random.choice(languages)
    matched_words = favorite_words.filter(language=random_language)

    query_string = urlencode({
        random_language.language_name: "true"
    })
    next_page = "http://testserver{}?{}".format(URL_GET, query_string)
    expected_previous_page = None

    number_pages = 0

    while next_page is not None:
        response = api_client.get(next_page, HTTP_AUTHORIZATION="Token {}".format(token))

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == len(matched_words)
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert result.get("language") == random_language.language_name
            assert favorite_words.filter(id=result.get("id"),
                                         language__language_name=result.get("language"),
                                         category__category_name=result.get("category"),
                                         word_name=result.get("word_name"),
                                         article__id=result.get("article")).exists()
            assert result.get("is_favorite")

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(len(matched_words)/12)


@pytest.mark.django_db
def test_favorite_words_get_with_search_filter(api_client, account, languages):
    """
    Checks that the endpoint returns only the favorite words that contain the specified search pattern when the search
    filter is specified.
    """
    user, password = account()[0]
    favorite_words = user.favorite_words.all()
    token = get_user_token(api_client, user, password)

    search_filter = get_random_string(1, string.ascii_letters)
    matched_words = favorite_words.filter(word_name__icontains=search_filter)

    query_params = {
        "search": search_filter
    }

    for language in languages.order_by("language_name"):
        query_params[language.language_name] = "true"

    url = get_alphabetically_ordered_url(URL_GET, query_params)
    next_page = "http://testserver{}".format(url)
    expected_previous_page = None

    number_pages = 0

    while next_page is not None:
        response = api_client.get(next_page, HTTP_AUTHORIZATION="Token {}".format(token))

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("count") == len(matched_words)
        assert response.data.get("previous") == (None if (expected_previous_page is None) else expected_previous_page)

        results = response.data.get("results")

        for result in results:
            assert search_filter.lower() in result.get("word_name").lower()
            assert favorite_words.filter(id=result.get("id"),
                                         language__language_name=result.get("language"),
                                         category__category_name=result.get("category"),
                                         word_name=result.get("word_name"),
                                         article__id=result.get("article")).exists()
            assert result.get("is_favorite")

        expected_previous_page = next_page
        next_page = response.data.get("next")
        number_pages += 1

    assert number_pages == math.ceil(len(matched_words)/12)
