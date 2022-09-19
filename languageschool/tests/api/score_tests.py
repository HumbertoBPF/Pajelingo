import random

import pytest
from django.db.models import Q
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Score
from languageschool.tests.utils import get_users, get_basic_auth_header, deserialize_data

URL = "/api/scores/"


@pytest.mark.django_db
def test_get_score_requires_authentication(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    score = random.choice(scores)

    response = api_client.get(URL + str(score.id))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_score_wrong_credentials(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    wrong_username = get_random_string(random.randint(1, 50))
    wrong_password = get_random_string(random.randint(1, 50))
    score = random.choice(scores)

    response = api_client.get(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(wrong_username, wrong_password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_score(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    score = random.choice(scores)

    response = api_client.get(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    json = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert json.get("id") == score.id
    assert json.get("user") == score.user.username
    assert json.get("language") == score.language.language_name
    assert json.get("game") == score.game.game_tag
    assert json.get("score") == score.score


@pytest.mark.django_db
def test_put_score_requires_authentication(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    score = random.choice(scores)

    response = api_client.put(URL + str(score.id))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_put_score_wrong_credentials(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    wrong_username = get_random_string(random.randint(1, 50))
    wrong_password = get_random_string(random.randint(1, 50))
    score = random.choice(scores)

    response = api_client.put(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(wrong_username, wrong_password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_put_score(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    score = random.choice(scores.filter(user=user))

    response = api_client.put(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    updated_score = Score.objects.get(pk=score.id)
    json = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert updated_score.score == score.score + 1
    assert updated_score.user.id == score.user.id
    assert updated_score.game.id == score.game.id
    assert updated_score.language.id == score.language.id
    assert json.get("score") == score.score + 1
    assert json.get("user") == score.user.username
    assert json.get("game") == score.game.game_tag
    assert json.get("language") == score.language.language_name


@pytest.mark.django_db
def test_put_score_user_does_not_own_score(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    score = random.choice(scores.filter(~Q(user=user)))

    response = api_client.put(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_score_endpoint_does_not_accept_post(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    score = random.choice(scores)

    response = api_client.post(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_score_endpoint_does_not_accept_delete(api_client, account, article_game, conjugation_game, vocabulary_game, languages, score):
    accounts = account(n=random.randint(1, 10))
    users = get_users(accounts)
    games = [article_game, conjugation_game, vocabulary_game]
    scores = score(users=users, games=games, languages=languages)

    user, password = random.choice(accounts)
    score = random.choice(scores)

    response = api_client.delete(URL+str(score.id), HTTP_AUTHORIZATION=get_basic_auth_header(user.username, password))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
