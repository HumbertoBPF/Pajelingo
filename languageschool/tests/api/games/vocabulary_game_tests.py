import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Word, Score
from languageschool.tests.utils import get_user_token

BASE_URL = reverse("vocabulary-game-api")


def get_correct_answer(word, base_language):
    for synonym in word.synonyms.all():
        if synonym.language.id == base_language.id:
            return synonym.word_name
    return ""


@pytest.mark.django_db
def test_vocabulary_game_setup_no_language(api_client):
    """
    Tests that a 404 Not Found is raised when no language is specified.
    """
    response = api_client.get(BASE_URL)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_vocabulary_game_setup_invalid_language(api_client):
    """
    Tests that a 404 Not Found is raised when an invalid language is specified.
    """
    query_string = urlencode({
        "language": get_random_string(8)
    })
    url = "{}?{}".format(BASE_URL, query_string)
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_vocabulary_game_setup(api_client, words, languages):
    """
    Tests that 200 Ok along with a random word id and name are returned when a valid language is specified.
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


@pytest.mark.parametrize("has_id", [True, False])
@pytest.mark.parametrize("has_base_language", [True, False])
@pytest.mark.parametrize("has_answer", [True, False])
@pytest.mark.django_db
def test_vocabulary_play_required_parameters(api_client, has_id, has_base_language, has_answer):
    """
    Checks that POST request to /api/vocabulary-game raise a 400 Bad Request when no word id, base language and answer
    parameters in the request body.
    """
    payload = {}

    if has_id:
        payload["word_id"] = random.randint(1, 1000)

    if has_base_language:
        payload["base_language"] = get_random_string(8)

    if has_answer:
        payload["answer"] = get_random_string(8)

    response = api_client.post(BASE_URL, data=payload)

    if has_id and has_base_language and has_answer:
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_vocabulary_play_invalid_word_id(api_client):
    """
    Checks that /api/vocabulary-game raises a 404 Not Found when an invalid word id is specified.
    """
    response = api_client.post(BASE_URL, data={
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

    response = api_client.post(BASE_URL, data={
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

    response = api_client.post(BASE_URL, data={
        "word_id": random_word.id,
        "base_language": get_random_string(8),
        "answer": get_random_string(8)
    })

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_vocabulary_play_not_authenticated_user(api_client, words, languages, is_correct):
    """
    Checks that POST requests to /api/vocabulary-play return 200 Ok along with the result, the correct answer, and the
    None as current score for non-authenticated users.
    """
    random_word = random.choice(words)

    eligible_languages = []

    for language in languages:
        if language.language_name != random_word.language.language_name:
            eligible_languages.append(language)

    random_base_language = random.choice(eligible_languages)

    correct_answer = get_correct_answer(random_word, random_base_language)

    response = api_client.post(BASE_URL, data={
        "word_id": random_word.id,
        "base_language": random_base_language.language_name,
        "answer": correct_answer if is_correct else get_random_string(8)
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("result") is is_correct
    assert response.data.get("correct_answer") == correct_answer
    assert response.data.get("score") is None


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_vocabulary_play_authenticated_user(api_client, account, words, languages, is_correct):
    """
    Checks that POST requests to /api/vocabulary-play return 200 Ok along with the result, the correct answer, and the
    current score for authenticated users.
    """
    user, password = account()[0]
    random_word = random.choice(words)

    eligible_languages = []

    for language in languages:
        if language.language_name != random_word.language.language_name:
            eligible_languages.append(language)

    random_base_language = random.choice(eligible_languages)

    correct_answer = get_correct_answer(random_word, random_base_language)

    token = get_user_token(api_client, user, password)

    response = api_client.post(BASE_URL, data={
        "word_id": random_word.id,
        "base_language": random_base_language.language_name,
        "answer": correct_answer if is_correct else get_random_string(8)
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("result") is is_correct
    assert response.data.get("correct_answer") == correct_answer
    if is_correct:
        assert Score.objects.filter(
            user__username=user.username,
            language=random_word.language,
            game__id=1,
            score=1
        ).exists()
        assert response.data.get("score") == 1
    else:
        assert response.data.get("score") is None
