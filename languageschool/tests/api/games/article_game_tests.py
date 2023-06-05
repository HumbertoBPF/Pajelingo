import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Word, Score, GameRound, Badge
from languageschool.tests.utils import get_user_token, achieve_explorer_badge

ARTICLE_GAME_URL = reverse("article-game-api")


@pytest.mark.django_db
def test_article_game_setup_with_no_language(api_client, languages, words):
    """
    Tests that a 404 Not Found is raised when no language name is provided.
    """
    response = api_client.get(ARTICLE_GAME_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_article_game_setup_with_invalid_language(api_client, languages, words):
    """
    Tests that a 404 Not Found is raised when an invalid language name is provided.
    """
    query_string = urlencode({
        "language": get_random_string(16)
    })
    url = "{}?{}".format(ARTICLE_GAME_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_article_game_setup_with_language_set_to_english(api_client, languages, words):
    """
    Tests that a 400 Bad Request is raised when the language specified in the URL is English.
    """
    query_string = urlencode({
        "language": "English"
    })
    url = "{}?{}".format(ARTICLE_GAME_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_article_game_setup_non_authenticated_user(api_client, languages, words):
    """
    Tests that 200 Ok along with a random word is returned when a valid language is specified.
    """
    random_language = random.choice(languages)

    query_string = urlencode({
        "language": random_language.language_name
    })
    url = "{}?{}".format(ARTICLE_GAME_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_body = response.data
    returned_word = Word.objects.get(id=response_body.get("id"))
    assert returned_word.word_name == response_body.get("word")
    assert returned_word.language == random_language


@pytest.mark.django_db
def test_article_game_setup_authenticated_user(api_client, account, languages, words):
    """
    Tests that 200 Ok along with a random word is returned when a valid language is specified, and that game round data
    is persisted.
    """
    user, password = account()[0]
    random_language = random.choice(languages)

    query_string = urlencode({
        "language": random_language.language_name
    })
    url = "{}?{}".format(ARTICLE_GAME_URL, query_string)
    response = api_client.get(url, HTTP_AUTHORIZATION="Token {}".format(get_user_token(api_client, user, password)))

    assert response.status_code == status.HTTP_200_OK

    response_body = response.data

    returned_word = Word.objects.get(id=response_body.get("id"))
    assert returned_word.word_name == response_body.get("word")
    assert returned_word.language == random_language

    assert GameRound.objects.filter(
        game__id=2,
        user=user,
        round_data={
            "word_id": response_body.get("id")
        }
    ).exists()


@pytest.mark.parametrize("has_word_id, has_answer", [
    (True, False),
    (False, True),
    (False, False)
])
@pytest.mark.django_db
def test_article_game_play_required_parameters(api_client, has_word_id, has_answer):
    """
    Tests that POST requests to /api/article-game require word_id and answer as parameters.
    """
    payload = {}

    if has_word_id:
        payload["word_id"] = random.randint(1, 1000)

    if has_answer:
        payload["answer"] = get_random_string(8)

    response = api_client.post(ARTICLE_GAME_URL, data=payload)

    assert response.status_code == response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_article_game_play_not_found_word(api_client):
    """
    Tests that a 404 Not Found is raised when the word id specified in the request body does not exist for POST
    requests to the endpoint /api/article-game.
    """
    response = api_client.post(ARTICLE_GAME_URL, data={
        "word_id": random.randint(1, 1000),
        "answer": get_random_string(8)
    })

    assert response.status_code == response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_article_game_play_not_authenticated_user(api_client, account, words, is_correct):
    """
    Tests that a 200 Ok is returned along with the result, the correct answer, and None as the current score by
    /api/article-game for unauthenticated requests.
    """
    user, _ = account()[0]
    achieve_explorer_badge(user)

    word = random.choice(words)

    response = api_client.post(ARTICLE_GAME_URL, data={
        "word_id": word.id,
        "answer": word.article.article_name if is_correct else get_random_string(8)
    })

    assert response.status_code == status.HTTP_200_OK
    response_body = response.data
    assert response_body.get("result") is is_correct
    assert response_body.get("correct_answer") == str(word)
    assert response_body.get("score") is None
    assert response_body.get("new_badges") == []


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_article_game_play_authenticated_user_without_game_round(api_client, account, words, is_correct):
    """
    Tests that a 403 Forbidden is returned by /api/article-game POST when no GET request was performed previously to
    get a word and consequently persist game round data.
    """
    user, password = account()[0]
    random_word = random.choice(words)

    token = get_user_token(api_client, user, password)

    response = api_client.post(ARTICLE_GAME_URL, data={
        "word_id": random_word.id,
        "answer": random_word.article.article_name if is_correct else get_random_string(8)
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_article_game_play_authenticated_user(api_client, account, words, is_correct):
    """
    Tests that a 200 Ok along with the result, the correct answer, and the current score is returned by
    /api/article-game for authenticated requests.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)

    random_word = random.choice(words)
    article_game_id = 2

    initial_score = Score.objects.filter(
        user=user,
        language=random_word.language,
        game__id=article_game_id
    ).first()

    GameRound.objects.create(
        game_id=article_game_id,
        user=user,
        round_data={
            "word_id": random_word.id
        }
    )

    token = get_user_token(api_client, user, password)

    response = api_client.post(ARTICLE_GAME_URL, data={
        "word_id": random_word.id,
        "answer": random_word.article.article_name if is_correct else get_random_string(8)
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_200_OK

    response_body = response.data

    assert response_body.get("result") is is_correct
    assert response_body.get("correct_answer") == str(random_word)

    if is_correct:
        expected_score = 1 if (initial_score is None) else initial_score.score + 1

        assert Score.objects.filter(
            user=user,
            language=random_word.language,
            game_id=article_game_id,
            score=expected_score
        ).exists()
        assert response_body.get("score") == expected_score

        new_badges = response_body.get("new_badges")

        assert len(new_badges) == 1
        assert Badge.objects.filter(
            name=new_badges[0].get("name"),
            color=new_badges[0].get("color"),
            description=new_badges[0].get("description")
        ).exists()
    else:
        assert response_body.get("score") is None
        assert response_body.get("new_badges") == []
    assert not GameRound.objects.filter(
        user=user,
        game_id=article_game_id
    ).exists()
