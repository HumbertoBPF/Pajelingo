import random

import pytest
from django.db.models import Q
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Score
from languageschool.tests.utils import get_users, get_basic_auth_header, get_random_username, get_valid_password
from languageschool.views.viewsets import CONFLICT_SCORE_MESSAGE, MISSING_PARAMETERS_SCORE_SEARCH_MESSAGE

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
    assert json.get("game") == game.id
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


@pytest.mark.django_db
def test_list_scores_create_score_requires_authentication(api_client, account):
    response = api_client.post(URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_scores_create_score_wrong_credentials(api_client, account):
    account()

    wrong_username = get_random_username()
    wrong_password = get_valid_password()
    response = api_client.post(URL, HTTP_AUTHORIZATION=get_basic_auth_header(wrong_username, wrong_password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_scores_create_score(api_client, account, games, languages):
    accounts = account(n=random.randint(1, 10))

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)
    data = {
        "language": language.language_name,
        "game": game.id
    }
    response = api_client.post(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    json = response.data

    assert response.status_code == status.HTTP_201_CREATED
    assert json.get("user") == user.username
    assert json.get("language") == language.language_name
    assert json.get("game") == game.id
    assert json.get("score") == 1


@pytest.mark.django_db
def test_list_scores_create_score_conflict(api_client, account, games, languages, score):
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

    response = api_client.post(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    json = response.data

    assert response.status_code == status.HTTP_409_CONFLICT
    assert json.get("error") == CONFLICT_SCORE_MESSAGE


@pytest.mark.parametrize(
    "has_language_key, has_game_key", [
        (False, False),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.django_db
def test_list_scores_create_score_bad_request(api_client, account, games, languages, has_language_key, has_game_key):
    accounts = account(n=random.randint(1, 10))

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {}
    if has_language_key:
        data["language"] = language.language_name
    if has_game_key:
        data["game"] = game.id

    response = api_client.post(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "is_valid_language, is_valid_game", [
        (False, False),
        (True, False),
        (False, False)
    ]
)
@pytest.mark.django_db
def test_list_scores_create_score_not_found(api_client, account, games, languages, is_valid_language, is_valid_game):
    accounts = account(n=random.randint(1, 10))

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {
        "language": language.language_name if is_valid_language else get_random_string(random.randint(10, 30)),
        "game": game.id if is_valid_game else random.randint(100, 300)
    }

    response = api_client.post(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_put_score_requires_authentication(api_client, account, games, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    scores = score(users=users, games=games, languages=languages)

    score = random.choice(scores)

    response = api_client.put(URL + str(score.id))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_put_score_wrong_credentials(api_client, account, games, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    scores = score(users=users, games=games, languages=languages)

    wrong_username = get_random_username()
    wrong_password = get_valid_password()
    score = random.choice(scores)

    response = api_client.put(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(wrong_username, wrong_password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_put_score(api_client, account, games, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    score = random.choice(scores.filter(user=user))

    response = api_client.put(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    updated_score = Score.objects.get(pk=score.id)
    json = response.data

    assert response.status_code == status.HTTP_200_OK
    assert updated_score.score == score.score + 1
    assert updated_score.user.id == score.user.id
    assert updated_score.game.id == score.game.id
    assert updated_score.language.id == score.language.id
    assert json.get("score") == score.score + 1
    assert json.get("user") == score.user.username
    assert json.get("game") == score.game.id
    assert json.get("language") == score.language.language_name


@pytest.mark.django_db
def test_put_score_user_does_not_own_score(api_client, account, games, languages, score):
    accounts = account(n=random.randint(2, 10))
    users = get_users(accounts)
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    score = random.choice(scores.filter(~Q(user=user)))

    response = api_client.put(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_score_endpoint_does_not_accept_delete(api_client, account, games, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    score = random.choice(scores)

    response = api_client.delete(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
