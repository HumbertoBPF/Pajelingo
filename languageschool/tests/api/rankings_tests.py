import math
import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from rest_framework import status

from languageschool.tests.utils import get_ranking

BASE_URL = reverse("rankings-api")


@pytest.mark.django_db
def test_rankings_api_response(api_client, languages):
    """
    Checks the response of the ranking API.
    """
    random_language = random.choice(languages)

    query_string = urlencode({"language": random_language.language_name})
    url = "{}?{}".format(BASE_URL, query_string)

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "next" in response.data.keys()
    assert "previous" in response.data.keys()
    assert "count" in response.data.keys()
    assert "results" in response.data.keys()


@pytest.mark.django_db
def test_all_ranking_scores(api_client, account, score, games, languages):
    """
    Checks that all the scores are returned in the correct order and with the expected content.
    """
    accounts = account(n=random.randint(21, 50))

    users = []

    for account in accounts:
        user, password = account
        users.append(user)

    score(users=users, games=games, languages=languages)

    random_language = random.choice(languages)

    expected_scores = get_ranking(random_language)

    query_string = urlencode({"language": random_language.language_name})
    url = "{}?{}".format(BASE_URL, query_string)

    response = api_client.get(url)

    count = response.data.get("count")
    number_pages = math.ceil(count/10)

    returned_scores = []

    for i in range(number_pages):
        query_string = urlencode({
            "language": random_language.language_name,
            "page": (i+1)
        })
        url = "{}?{}".format(BASE_URL, query_string)
        response = api_client.get(url)
        returned_scores = returned_scores + response.data.get("results")

    assert len(returned_scores) == len(expected_scores)

    for i in range(len(returned_scores)):
        assert returned_scores[i].get("position") == (i+1)
        assert returned_scores[i].get("user") == expected_scores[i].get("user__username")
        assert returned_scores[i].get("score") == expected_scores[i].get("score")


@pytest.mark.django_db
def test_all_pages(api_client, account, score, games, languages):
    """
    Checks the response of all pages requested (previous and next links, and the count)
    """
    accounts = account(n=random.randint(21, 50))

    users = []

    for account in accounts:
        user, password = account
        users.append(user)

    score(users=users, games=games, languages=languages)

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
