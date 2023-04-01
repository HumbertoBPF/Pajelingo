import random

import pytest
from rest_framework import status

from languageschool.tests.utils import get_users, get_basic_auth_header, get_random_username, get_valid_password
from languageschool.views import MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE

URL = "/api/score/"


@pytest.mark.django_db
def test_get_score_requires_authentication(api_client, account, games, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    scores = score(users=users, games=games, languages=languages)

    score = random.choice(scores)

    response = api_client.get(URL + str(score.id))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_score_wrong_credentials(api_client, account, games, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    scores = score(users=users, games=games, languages=languages)

    wrong_username = get_random_username()
    wrong_password = get_valid_password()
    score = random.choice(scores)

    response = api_client.get(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(wrong_username, wrong_password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_scores_get_score(api_client, account, games, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {
        "language": language.language_name,
        "game": game.id
    }

    response = api_client.get(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

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
def test_list_scores_get_score_missing_parameters(api_client, account, games, languages, score, has_language, has_game):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {}

    if has_language:
        data["language"] = language.language_name

    if has_game:
        data["game"] = game.id

    response = api_client.get(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    json = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.get("error") == MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE
