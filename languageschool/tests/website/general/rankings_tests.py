import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status


def access_rankings(client, accounts, games, languages, score, language_name):
    users = []

    for user, password in accounts:
        users.append(user)

    score(users=users, games=games, languages=languages)

    url = reverse('rankings')
    data = {}

    if language_name is not None:
        data["language"] = language_name

    response = client.get(url, data=data)

    scores = response.context.get("scores")

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get("languages"), languages, ordered=False)
    if language_name is not None:
        assert response.context.get("language").language_name == language_name
    assert len(scores) == min(len(accounts), 10)
    # Checking if the scores are in decreasing order
    last_score = scores[0]
    for i in range(1, len(scores)):
        assert last_score.get("score") >= scores[i].get("score")
        last_score = scores[i]

    return response


@pytest.mark.parametrize(
    "has_language_filter", [True, False]
)
@pytest.mark.django_db
def test_rankings(client, account, games, languages, score, has_language_filter):
    accounts = account(n=random.randint(5, 30))
    language_name = random.choice(languages).language_name if has_language_filter else None
    access_rankings(client, accounts, games, languages, score, language_name)


@pytest.mark.django_db
def test_rankings_invalid_language_filter(client, account, games, languages, score):
    url = reverse('rankings')
    data = {"language": get_random_string(random.randint(10, 30))}

    response = client.get(url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "has_language_filter", [True, False]
)
@pytest.mark.django_db
def test_rankings_authenticated_user(client, account, games, languages, score, has_language_filter):
    accounts = account(n=random.randint(5, 30))
    user, password = accounts[0]
    language_name = random.choice(languages).language_name if has_language_filter else None

    client.login(username=user.username, password=password)

    response = access_rankings(client, accounts, games, languages, score, language_name)

    assert response.context.get('my_position') is not None
    assert response.context.get('my_score') is not None
