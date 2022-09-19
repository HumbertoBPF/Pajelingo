import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.tests.api.comparers import ListScoresComparer
from languageschool.tests.utils import get_basic_auth_header, deserialize_data, \
    is_model_objects_equal_to_dict_array, get_users
from languageschool.views.viewsets import CONFLICT_SCORE_MESSAGE

URL = reverse("list-scores-api")


@pytest.mark.django_db
def test_list_scores_requires_authentication(api_client, account):
    response = api_client.get(URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_scores_wrong_credentials(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    user, password = account()[0]
    score(users=[user], games=[article_game, conjugation_game, vocabulary_game], languages=languages)

    wrong_username = get_random_string(random.randint(1, 50))
    wrong_password = get_random_string(random.randint(1, 50))
    response = api_client.get(URL, HTTP_AUTHORIZATION=get_basic_auth_header(wrong_username, wrong_password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_scores(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    games = [article_game, conjugation_game, vocabulary_game]
    users = get_users(accounts)
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)

    response = api_client.get(URL, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(scores, data, ListScoresComparer())


@pytest.mark.django_db
def test_list_scores_get_score(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    games = [article_game, conjugation_game, vocabulary_game]
    users = get_users(accounts)
    score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {
        "language_id": language.id,
        "game": game.game_tag
    }

    response = api_client.get(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    data = deserialize_data(response.data)
    json = data[0]

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 1
    assert json.get("user") == user.username
    assert json.get("language") == language.language_name
    assert json.get("game") == game.game_tag
    assert json.get("score") is not None


@pytest.mark.django_db
def test_list_scores_create_score_requires_authentication(api_client, account):
    response = api_client.post(URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_scores_create_score_wrong_credentials(api_client, account):
    account()

    wrong_username = get_random_string(random.randint(1, 50))
    wrong_password = get_random_string(random.randint(1, 50))
    response = api_client.post(URL, HTTP_AUTHORIZATION=get_basic_auth_header(wrong_username, wrong_password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_scores_create_score(api_client, account, article_game, conjugation_game, vocabulary_game, languages):
    accounts = account(n=random.randint(1, 10))
    games = [article_game, conjugation_game, vocabulary_game]

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)
    data = {
        "language": language.language_name,
        "game": game.game_tag
    }
    response = api_client.post(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    json = deserialize_data(response.data)

    assert response.status_code == status.HTTP_201_CREATED
    assert json.get("user") == user.username
    assert json.get("language") == language.language_name
    assert json.get("game") == game.game_tag
    assert json.get("score") == 1


@pytest.mark.django_db
def test_list_scores_create_score_conflict(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    games = [article_game, conjugation_game, vocabulary_game]
    users = get_users(accounts)

    score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {
        "language": language.language_name,
        "game": game.game_tag
    }

    response = api_client.post(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    json = deserialize_data(response.data)

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
def test_list_scores_create_score_bad_request(api_client, account, article_game, conjugation_game, vocabulary_game, languages, has_language_key, has_game_key):
    accounts = account(n=random.randint(1, 10))
    games = [article_game, conjugation_game, vocabulary_game]

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {}
    if has_language_key:
        data["language"] = language.language_name
    if has_game_key:
        data["game"] = game.game_tag

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
def test_list_scores_create_score_not_found(api_client, account, article_game, conjugation_game, vocabulary_game, languages, is_valid_language, is_valid_game):
    accounts = account(n=random.randint(1, 10))
    games = [article_game, conjugation_game, vocabulary_game]

    user, password = random.choice(accounts)
    language = random.choice(languages)
    game = random.choice(games)

    data = {
        "language": language.language_name if is_valid_language else get_random_string(random.randint(10, 30)),
        "game": game.game_tag if is_valid_game else get_random_string(random.randint(10, 30))
    }

    response = api_client.post(URL, data=data, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_list_scores_does_not_accept_put(api_client, account, article_game, conjugation_game, vocabulary_game, languages):
    accounts = account(n=random.randint(1, 10))

    user, password = random.choice(accounts)

    response = api_client.put(URL, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_list_scores_does_not_accept_delete(api_client, account, article_game, conjugation_game, vocabulary_game, languages):
    accounts = account(n=random.randint(1, 10))

    user, password = random.choice(accounts)

    response = api_client.delete(URL, HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
