import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status


def access_rankings(client, accounts, vocabulary_game, article_game, conjugation_game, languages, score, language):
    users = []

    for user, password in accounts:
        users.append(user)

    score(users=users, games=[vocabulary_game, article_game, conjugation_game], languages=languages)

    url = reverse('rankings')
    data = {}

    if language is not None:
        data["language"] = language

    response = client.get(url, data=data)

    scores = response.context.get("scores")

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get("languages"), languages, ordered=False)
    if language is not None:
        assert response.context.get("language").language_name == language
    assert len(scores) == min(len(accounts), 10)
    # Checking if the scores are in decreasing order
    last_score = scores[0]
    for i in range(1, len(scores)):
        assert last_score.get("score") >= scores[i].get("score")
        last_score = scores[i]

    return response


@pytest.mark.parametrize(
    "language", [
        None,
        "English",
        "Spanish",
        "Portuguese",
        "French",
        "German"
    ]
)
@pytest.mark.django_db
def test_rankings(client, account, vocabulary_game, article_game, conjugation_game, languages, score, language):
    accounts = account(n=random.randint(5, 30))
    access_rankings(client, accounts, vocabulary_game, article_game, conjugation_game, languages, score, language)


@pytest.mark.django_db
def test_rankings_invalid_language_filter(client, account, vocabulary_game, article_game, conjugation_game, languages, score):
    url = reverse('rankings')
    data = {"language": get_random_string(random.randint(10, 30))}

    response = client.get(url, data=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "language", [
        None,
        "English",
        "Spanish",
        "Portuguese",
        "French",
        "German"
    ]
)
@pytest.mark.django_db
def test_rankings_authenticated_user(client, account, vocabulary_game, article_game, conjugation_game, languages, score, language):
    accounts = account(n=random.randint(5, 30))
    user, password = accounts[0]
    client.login(username=user.username, password=password)

    response = access_rankings(client, accounts, vocabulary_game, article_game, conjugation_game, languages, score, language)

    assert response.context.get('my_position') is not None
    assert response.context.get('my_score') is not None
