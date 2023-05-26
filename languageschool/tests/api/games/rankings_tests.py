import math
import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.tests.utils import get_ranking, get_users

BASE_URL = reverse("rankings-api")


@pytest.mark.django_db
def test_get_rankings_without_language_param(api_client):
    """
    Checks that if no language is specified as GET param, then a 404 Not Found is returned.
    """
    response = api_client.get(BASE_URL)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_rankings_invalid_language_param(api_client):
    """
    Checks that if a invalid language is specified as GET param, then a 404 Not Found is returned.
    """
    query_string = urlencode({"language": get_random_string(16)})
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_rankings_invalid_user_param(api_client, languages):
    """
    Checks that if a invalid user is specified as GET param, then a 404 Not Found is returned.
    """
    query_string = urlencode({
        "language": random.choice(languages).language_name,
        "user": get_random_string(16)
    })
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize("is_authenticated", [True, False])
def test_get_rankings_check_response_params(api_client, account, score, languages, is_authenticated):
    """
    Checks the response of the ranking API.
    """
    accounts = account(n=random.randint(21, 50))

    users = get_users(accounts)

    score(users=users, languages=languages)

    random_language = random.choice(languages)

    query_params = {"language": random_language.language_name}

    if is_authenticated:
        authenticated_user, password = random.choice(accounts)
        query_params["user"] = authenticated_user.username

    query_string = urlencode(query_params)
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "next" in response.data.keys()
    assert "previous" in response.data.keys()
    assert "count" in response.data.keys()
    assert "results" in response.data.keys()
    assert (response.data.get("user_score") is not None) is is_authenticated


@pytest.mark.django_db
@pytest.mark.parametrize("is_authenticated", [True, False])
def test_get_rankings_scores(api_client, account, score, languages, is_authenticated):
    """
    Checks that all the scores are returned in the correct order and with the expected content.
    """
    accounts = account(n=random.randint(21, 50))
    authenticated_user = random.choice(accounts)[0] if is_authenticated else None

    users = get_users(accounts)

    score(users=users, languages=languages)

    random_language = random.choice(languages)

    expected_scores = get_ranking(random_language)

    query_params = {"language": random_language.language_name}

    if is_authenticated:
        query_params["user"] = authenticated_user.username

    query_string = urlencode(query_params)
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)

    returned_user_score = response.data.get("user_score")

    count = response.data.get("count")
    number_pages = math.ceil(count/10)

    returned_scores = []

    for i in range(number_pages):
        query_params = {
            "language": random_language.language_name,
            "page": (i+1)
        }

        if is_authenticated:
            query_params["user"] = authenticated_user.username

        query_string = urlencode(query_params)
        url = "{}?{}".format(BASE_URL, query_string)
        response = api_client.get(url)

        returned_scores = returned_scores + response.data.get("results")
        assert response.data.get("user_score") == returned_user_score

    assert len(returned_scores) == len(expected_scores)

    user_score = None

    for i in range(len(returned_scores)):
        user = returned_scores[i].get("user")
        if is_authenticated and (user == query_params.get("user")):
            user_score = {
                "position": returned_scores[i].get("position"),
                "user": returned_scores[i].get("user"),
                "score": returned_scores[i].get("score")
            }

        assert returned_scores[i].get("position") == (i+1)
        assert user == expected_scores[i].get("user__username")
        assert returned_scores[i].get("score") == expected_scores[i].get("score")

    assert returned_user_score == user_score


@pytest.mark.django_db
def test_get_rankings_pagination(api_client, account, score, languages):
    """
    Checks the response of all pages requested (previous and next links, and the count)
    """
    accounts = account(n=random.randint(21, 50))

    users = get_users(accounts)

    score(users=users, languages=languages)

    random_language = random.choice(languages)
    expected_scores = get_ranking(random_language)

    query_string = urlencode({"language": random_language.language_name})
    url = "{}?{}".format(BASE_URL, query_string)

    response = api_client.get(url)

    count = response.data.get("count")
    number_pages = math.ceil(count/10)

    for i in range(number_pages):
        page = i + 1
        query_string = urlencode({
            "language": random_language.language_name,
            "page": page
        })
        url = "{}?{}".format(BASE_URL, query_string)
        response = api_client.get(url)

        url_params = {
            "language": random_language.language_name
        }
        if page != 2:
            url_params["page"] = page - 1
        query_string = urlencode(url_params)

        expected_previous_url = None if (page == 1) else "http://testserver{}?{}".format(BASE_URL, query_string)

        query_string = urlencode({
            "language": random_language.language_name,
            "page": (page + 1)
        })
        expected_next_url = None if (page == number_pages) else "http://testserver{}?{}".format(BASE_URL, query_string)

        assert response.data.get("previous") == (None if (page == 1) else expected_previous_url)
        assert response.data.get("next") == (None if (page == number_pages) else expected_next_url)
        assert response.data.get("count") == len(expected_scores)
