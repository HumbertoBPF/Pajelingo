import random

import pytest
from rest_framework import status

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
def test_list_scores_get_score(api_client, account, languages, score, games):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    score(users=users, languages=languages)

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {
        "language": language.language_name,
        "game": game.id
    }

    token = get_user_token(api_client, user, password)

    response = api_client.get(URL, data=data, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data
    json = response_body[0]

    assert response.status_code == status.HTTP_200_OK
    assert len(response_body) == 1
    assert json.get("user") == user.username
    assert json.get("language") == language.language_name
    assert json.get("game") == game.game_name
    assert json.get("score") is not None


@pytest.mark.django_db
@pytest.mark.parametrize("field", ["language", "game"])
def test_list_scores_get_score_missing_parameters(api_client, account, languages, score, games, field):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    score(users=users, languages=languages)

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {
        "language": language.language_name,
        "game": game.id
    }

    del data[field]

    token = get_user_token(api_client, user, password)

    response = api_client.get(URL, data=data, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_body.get("error") == MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE
