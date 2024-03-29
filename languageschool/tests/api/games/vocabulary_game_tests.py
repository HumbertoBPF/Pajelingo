import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Word, Score, GameRound, Badge
from languageschool.tests.utils import get_user_token, get_vocabulary_game_answer, achieve_explorer_badge

VOCABULARY_GAME_URL = reverse("vocabulary-game-api")


@pytest.mark.parametrize("has_base_language, has_target_language", [
    (False, True),
    (True, False),
    (False, False)
])
@pytest.mark.django_db
def test_vocabulary_game_setup_missing_arguments(api_client, has_base_language, has_target_language):
    """
    Tests that a 404 Not Found is raised when no language is specified.
    """
    query_dict = {}

    if has_base_language:
        query_dict["base_language"] = get_random_string(8)

    if has_target_language:
        query_dict["target_language"] = get_random_string(8)

    query_string = urlencode(query_dict)
    url = "{}?{}".format(VOCABULARY_GAME_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("has_valid_base_language, has_valid_target_language", [
    (False, True),
    (True, False),
    (False, False)
])
@pytest.mark.django_db
def test_vocabulary_game_setup_invalid_language(api_client, languages, has_valid_base_language,
                                                has_valid_target_language):
    """
    Tests that a 404 Not Found is raised when an invalid language is specified.
    """
    random_base_language = random.choice(languages)
    random_target_language = random.choice(languages.exclude(id=random_base_language.id))

    query_string = urlencode({
        "base_language": random_base_language.language_name if has_valid_base_language else get_random_string(8),
        "target_language": random_target_language.language_name if has_valid_target_language else get_random_string(8)
    })
    url = "{}?{}".format(VOCABULARY_GAME_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_vocabulary_game_setup_non_authenticated_user(api_client, words, languages):
    """
    Tests that 200 Ok along with a random word id and name are returned when a valid language is specified.
    """
    random_base_language = random.choice(languages)
    random_target_language = random.choice(languages.exclude(id=random_base_language.id))

    query_string = urlencode({
        "base_language": random_base_language.language_name,
        "target_language": random_target_language.language_name
    })
    url = "{}?{}".format(VOCABULARY_GAME_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    response_body = response.data

    assert Word.objects.filter(
        id=response_body.get("id"),
        word_name=response_body.get("word"),
        language=random_target_language
    ).exists()


@pytest.mark.django_db
def test_vocabulary_game_setup_authenticated_user(api_client, account, words, languages):
    """
    Tests that 200 Ok along with a random word id and name are returned when a valid language is specified, and that
    data concerning this game round is persisted.
    """
    user, password = account()[0]

    random_base_language = random.choice(languages)
    random_target_language = random.choice(languages.exclude(id=random_base_language.id))

    query_string = urlencode({
        "base_language": random_base_language.language_name,
        "target_language": random_target_language.language_name
    })
    url = "{}?{}".format(VOCABULARY_GAME_URL, query_string)
    response = api_client.get(url, HTTP_AUTHORIZATION="Token {}".format(get_user_token(api_client, user, password)))

    assert response.status_code == status.HTTP_200_OK

    response_body = response.data

    assert Word.objects.filter(
        id=response_body.get("id"),
        word_name=response_body.get("word"),
        language=random_target_language
    ).exists()
    assert GameRound.objects.filter(
        game__id=1,
        user=user,
        round_data={
            "word_id": response_body.get("id"),
            "base_language": random_base_language.language_name
        }
    ).exists()


@pytest.mark.parametrize("field", ["word_id", "base_language", "answer"])
@pytest.mark.django_db
def test_vocabulary_play_required_parameters(api_client, field):
    """
    Checks that POST request to /api/vocabulary-game raise a 400 Bad Request when no word id, base language and answer
    parameters in the request body.
    """
    payload = {
        "word_id": random.randint(1, 1000),
        "base_language": get_random_string(8),
        "answer": get_random_string(8)
    }

    del payload[field]

    response = api_client.post(VOCABULARY_GAME_URL, data=payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body[field]) == 1
    assert str(response_body[field][0]) == "This field is required."


@pytest.mark.django_db
def test_vocabulary_play_invalid_word_id(api_client):
    """
    Checks that /api/vocabulary-game raises a 404 Not Found when an invalid word id is specified.
    """
    response = api_client.post(VOCABULARY_GAME_URL, data={
        "word_id": random.randint(1, 1000),
        "base_language": get_random_string(8),
        "answer": get_random_string(8)
    })

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_vocabulary_play_base_and_target_language_are_the_same(api_client, words):
    """
    Checks that /api/vocabulary-game raises a 400 Bad Request when the base language (language of the word whose id
    was specified) and the target languages are the same.
    """
    random_word = random.choice(words)

    response = api_client.post(VOCABULARY_GAME_URL, data={
        "word_id": random_word.id,
        "base_language": random_word.language.language_name,
        "answer": get_random_string(8)
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get("non_field_errors")[0] == "Base and target languages must not be equal."


@pytest.mark.django_db
def test_vocabulary_play_invalid_base_language(api_client, words):
    """
    Checks that /api/vocabulary-game raises a 404 Not Found when the base language parameter does not match any
    language.
    """
    random_word = random.choice(words)

    response = api_client.post(VOCABULARY_GAME_URL, data={
        "word_id": random_word.id,
        "base_language": get_random_string(8),
        "answer": get_random_string(8)
    })

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_vocabulary_play_not_authenticated_user(api_client, words, languages, account, is_correct):
    """
    Checks that POST requests to /api/vocabulary-play return 200 Ok along with the result, the correct answer, and the
    None as current score for non-authenticated users.
    """
    user, _ = account()[0]
    achieve_explorer_badge(user)

    random_word = random.choice(words)
    random_base_language = random.choice(languages.exclude(id=random_word.language_id))

    correct_answer = get_vocabulary_game_answer(random_word, random_base_language)

    response = api_client.post(VOCABULARY_GAME_URL, data={
        "word_id": random_word.id,
        "base_language": random_base_language.language_name,
        "answer": correct_answer if is_correct else get_random_string(8)
    })

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert response_body.get("result") is is_correct
    assert response_body.get("correct_answer") == f"{random_word.word_name}: {correct_answer}"
    assert response_body.get("score") is None
    assert response_body.get("new_badges") == []


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_vocabulary_play_authenticated_user_without_game_round(api_client, account, words, languages, is_correct):
    """
    Checks that POST requests to /api/vocabulary-play return 403 Forbidden when no GET request was performed previously
    to get a word and consequently persist game round data.
    """
    user, password = account()[0]

    random_word = random.choice(words)
    random_base_language = random.choice(languages.exclude(id=random_word.language_id))

    correct_answer = get_vocabulary_game_answer(random_word, random_base_language)

    token = get_user_token(api_client, user, password)

    response = api_client.post(VOCABULARY_GAME_URL, data={
        "word_id": random_word.id,
        "base_language": random_base_language.language_name,
        "answer": correct_answer if is_correct else get_random_string(8)
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_vocabulary_play_authenticated_user(api_client, account, words, languages, is_correct):
    """
    Checks that POST requests to /api/vocabulary-play return 200 Ok along with the result, the correct answer, and the
    current score for authenticated users.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)

    vocabulary_game_id = 1

    random_word = random.choice(words)
    random_base_language = random.choice(languages.exclude(id=random_word.language_id))

    correct_answer = get_vocabulary_game_answer(random_word, random_base_language)

    initial_score = Score.objects.filter(
        user=user,
        language=random_word.language,
        game__id=vocabulary_game_id
    ).first()

    GameRound.objects.create(
        game_id=vocabulary_game_id,
        user=user,
        round_data={
            "word_id": random_word.id,
            "base_language": random_base_language.language_name
        }
    )

    token = get_user_token(api_client, user, password)

    response = api_client.post(VOCABULARY_GAME_URL, data={
        "word_id": random_word.id,
        "base_language": random_base_language.language_name,
        "answer": correct_answer if is_correct else get_random_string(8)
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert response_body.get("result") is is_correct
    assert response_body.get("correct_answer") == f"{random_word.word_name}: {correct_answer}"
    if is_correct:
        expected_score = 1 if (initial_score is None) else initial_score.score + 1

        assert Score.objects.filter(
            user=user,
            language=random_word.language,
            game_id=vocabulary_game_id,
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
        game_id=vocabulary_game_id
    ).exists()
