import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Word, Game, Score
from languageschool.tests.utils import get_user_token

BASE_URL = reverse("article-game-api")


@pytest.mark.django_db
def test_article_game_setup_with_no_language(api_client, games, languages, words):
    """
    Tests that a 404 Not Found is raised when no language name is provided.
    """
    response = api_client.get(BASE_URL)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_article_game_setup_with_invalid_language(api_client, games, languages, words):
    """
    Tests that a 404 Not Found is raised when an invalid language name is provided.
    """
    query_string = urlencode({
        "language": get_random_string(16)
    })
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_article_game_setup_with_language_set_to_english(api_client, games, languages, words):
    """
    Tests that a 400 Bad Request is raised when the language specified in the URL is English.
    """
    query_string = urlencode({
        "language": "English"
    })
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_article_game_setup(api_client, games, languages, words):
    """
    Tests that 200 Ok along with a random word is returned when a valid language is specified.
    """
    random_language = random.choice(languages)

    query_string = urlencode({
        "language": random_language.language_name
    })
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    returned_word = response.data
    assert Word.objects.filter(
        id=returned_word.get("id"),
        word_name=returned_word.get("word"),
        language=random_language
    ).exists()


@pytest.mark.parametrize("has_word_id, has_answer", [
    (True, False),
    (False, True),
    (False, False)
])
@pytest.mark.django_db
def test_article_game_play_required_parameters(api_client, games, has_word_id, has_answer):
    """
    Tests that POST requests to /api/article-game require word_id and answer as parameters.
    """
    payload = {}

    if has_word_id:
        payload["word_id"] = random.randint(1, 1000)

    if has_answer:
        payload["answer"] = get_random_string(8)

    response = api_client.post(BASE_URL, data=payload)

    assert response.status_code == response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_article_game_play_not_found_word(api_client, games):
    """
    Tests that a 404 Not Found is raised when the word id specified in the request body does not exist for POST
    requests to the endpoint /api/article-game.
    """
    response = api_client.post(BASE_URL, data={
        "word_id": random.randint(1, 1000),
        "answer": get_random_string(8)
    })

    assert response.status_code == response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_article_game_play_not_authenticated_user(api_client, games, words, is_correct):
    """
    Tests that a 200 Ok is returned along with the result, the correct answer, and None as the current score by
    /api/article-game for unauthenticated requests.
    """
    word = random.choice(words)

    response = api_client.post(BASE_URL, data={
        "word_id": word.id,
        "answer": word.article.article_name if is_correct else get_random_string(8)
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("result") is is_correct
    assert response.data.get("correct_answer") == str(word)
    assert response.data.get("score") is None


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_article_game_play_authenticated_user(api_client, article_game, account, words, is_correct):
    """
    Tests that a 200 Ok along with the result, the correct answer, and the current score is returned by
    /api/article-game for authenticated requests.
    """
    user, password = account()[0]
    random_word = random.choice(words)

    token = get_user_token(api_client, user, password)

    response = api_client.post(BASE_URL, data={
        "word_id": random_word.id,
        "answer": random_word.article.article_name if is_correct else get_random_string(8)
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("result") is is_correct
    assert response.data.get("correct_answer") == str(random_word)

    if is_correct:
        assert Score.objects.filter(
            user__username=user.username,
            language=random_word.language,
            game=article_game,
            score=1
        ).exists()
        assert response.data.get("score") == 1
    else:
        assert response.data.get("score") is None
