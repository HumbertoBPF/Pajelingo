import random

import pytest
from rest_framework import status

from languageschool.models import Game
from languageschool.tests.utils import get_users, get_user_token
from languageschool.views import MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE

URL = "/api/score/"


@pytest.mark.django_db
def test_get_score_requires_authentication(api_client, account, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    score(users=users, languages=languages)

    response = api_client.get(URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_scores_get_score(api_client, account, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    score(users=users, languages=languages)

    user, password = random.choice(accounts)
    language = random.choice(languages)
    print(Game.objects.all())
    game = random.choice(Game.objects.all())

    data = {
        "language": language.language_name,
        "game": game.id
    }

    token = get_user_token(api_client, user, password)

    response = api_client.get(URL, data=data, HTTP_AUTHORIZATION="Token {}".format(token))

    data = response.data
    json = data[0]

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert json.get("user") == user.username
    assert json.get("language") == language.language_name
    assert json.get("game") == game.game_name
    assert json.get("score") is not None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "has_language, has_game", [
        (False, False),
        (True, False),
        (False, True)
    ]
)
def test_list_scores_get_score_missing_parameters(api_client, account, languages, score, has_language, has_game):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    score(users=users, languages=languages)

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(Game.objects.all())

    data = {}

    if has_language:
        data["language"] = language.language_name

    if has_game:
        data["game"] = game.id

    token = get_user_token(api_client, user, password)

    response = api_client.get(URL, data=data, HTTP_AUTHORIZATION="Token {}".format(token))

    json = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.get("error") == MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE
