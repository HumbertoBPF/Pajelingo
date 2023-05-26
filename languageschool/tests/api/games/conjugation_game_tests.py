import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Conjugation, Score, GameRound, Game
from languageschool.tests.utils import get_user_token

BASE_URL = reverse("conjugation-game-api")


def get_correct_answer(conjugation):
    language = conjugation.word.language

    return "{} {}\n{} {}\n{} {}\n{} {}\n{} {}\n{} {}\n"\
        .format(language.personal_pronoun_1, conjugation.conjugation_1,
                language.personal_pronoun_2, conjugation.conjugation_2,
                language.personal_pronoun_3, conjugation.conjugation_3,
                language.personal_pronoun_4, conjugation.conjugation_4,
                language.personal_pronoun_5, conjugation.conjugation_5,
                language.personal_pronoun_6, conjugation.conjugation_6)


@pytest.mark.django_db
def test_conjugation_game_setup_no_language(api_client):
    """
    Checks that /api/conjugation-game raises a 404 Not Found when no language is specified.
    """
    response = api_client.get(BASE_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_conjugation_game_setup_invalid_language(api_client):
    """
    Checks that /api/conjugation-game raises a 404 Not Found when a invalid language is specified.
    """
    query_string = urlencode({
        "language": get_random_string(8)
    })
    url = "{}?{}".format(BASE_URL, query_string)

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_conjugation_game_setup_non_authenticated_user(api_client, verbs, languages, conjugations):
    """
    Checks that a 200 Ok is returned by /api/conjugation-game along with a random verb and one of its conjugations
    when a valid language is specified.
    """
    random_language = random.choice(languages)

    query_string = urlencode({
        "language": random_language.language_name
    })
    url = "{}?{}".format(BASE_URL, query_string)

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_body = response.data
    assert Conjugation.objects.filter(
        word__id=response_body.get("id"),
        word__word_name=response_body.get("word"),
        word__language=random_language,
        tense=response_body.get("tense")
    ).exists()


@pytest.mark.django_db
def test_conjugation_game_setup_authenticated_user(api_client, account, verbs, languages, conjugations):
    """
    Checks that a 200 Ok is returned by /api/conjugation-game along with a random verb and one of its conjugations
    when a valid language is specified, and that data concerning this game round is persisted.
    """
    user, password = account()[0]
    random_language = random.choice(languages)

    query_string = urlencode({
        "language": random_language.language_name
    })
    url = "{}?{}".format(BASE_URL, query_string)

    response = api_client.get(url, HTTP_AUTHORIZATION="Token {}".format(get_user_token(api_client, user, password)))

    assert response.status_code == status.HTTP_200_OK
    response_body = response.data
    assert Conjugation.objects.filter(
        word__id=response_body.get("id"),
        word__word_name=response_body.get("word"),
        word__language=random_language,
        tense=response_body.get("tense")
    ).exists()
    assert GameRound.objects.filter(
        game__id=3,
        user=user,
        round_data={
            "word_id": response_body.get("id"),
            "tense": response_body.get("tense")
        }
    )


@pytest.mark.parametrize("has_id", [True, False])
@pytest.mark.parametrize("has_tense", [True, False])
@pytest.mark.parametrize("has_conjugation_1", [True, False])
@pytest.mark.parametrize("has_conjugation_2", [True, False])
@pytest.mark.parametrize("has_conjugation_3", [True, False])
@pytest.mark.parametrize("has_conjugation_4", [True, False])
@pytest.mark.parametrize("has_conjugation_5", [True, False])
@pytest.mark.parametrize("has_conjugation_6", [True, False])
@pytest.mark.django_db
def test_conjugation_game_play_required_parameters(api_client, has_id, has_tense, has_conjugation_1,
                                                   has_conjugation_2, has_conjugation_3, has_conjugation_4,
                                                   has_conjugation_5, has_conjugation_6):
    """
    Checks that /api/conjugation-game returns 400 Bad Request when some required parameter is missing.
    """
    payload = {}

    if has_id:
        payload["word_id"] = random.randint(1, 1000)

    if has_tense:
        payload["tense"] = get_random_string(8)

    if has_conjugation_1:
        payload["conjugation_1"] = get_random_string(8)

    if has_conjugation_2:
        payload["conjugation_2"] = get_random_string(8)

    if has_conjugation_3:
        payload["conjugation_3"] = get_random_string(8)

    if has_conjugation_4:
        payload["conjugation_4"] = get_random_string(8)

    if has_conjugation_5:
        payload["conjugation_5"] = get_random_string(8)

    if has_conjugation_6:
        payload["conjugation_6"] = get_random_string(8)

    response = api_client.post(BASE_URL, data=payload)

    if has_id and has_tense and has_conjugation_1 and has_conjugation_2 and has_conjugation_3 and has_conjugation_4 \
            and has_conjugation_5 and has_conjugation_6:
        assert response.status_code == status.HTTP_404_NOT_FOUND
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_conjugation_game_play_invalid_verb(api_client):
    """
    Checks that /api/conjugation-game raises a 404 Not Found when the specified word id does not match any verb.
    """
    response = api_client.post(BASE_URL, data={
        "word_id": random.randint(1, 1000),
        "tense": get_random_string(8),
        "conjugation_1": get_random_string(8),
        "conjugation_2": get_random_string(8),
        "conjugation_3": get_random_string(8),
        "conjugation_4": get_random_string(8),
        "conjugation_5": get_random_string(8),
        "conjugation_6": get_random_string(8)
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_conjugation_game_play_invalid_conjugation(api_client, conjugations):
    """
    Checks that /api/conjugation-game raises a 404 Not Found when the specified verb and tense do not match any
    conjugation.
    """
    random_conjugation = random.choice(conjugations)

    response = api_client.post(BASE_URL, data={
        "word_id": random_conjugation.word_id,
        "tense": get_random_string(8),
        "conjugation_1": get_random_string(8),
        "conjugation_2": get_random_string(8),
        "conjugation_3": get_random_string(8),
        "conjugation_4": get_random_string(8),
        "conjugation_5": get_random_string(8),
        "conjugation_6": get_random_string(8)
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("has_correct_conjugation_1", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_2", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_3", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_4", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_5", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_6", [True, False])
@pytest.mark.django_db
def test_conjugation_game_play_non_authenticated_user(api_client, verbs, conjugations, has_correct_conjugation_1,
                                                      has_correct_conjugation_2, has_correct_conjugation_3,
                                                      has_correct_conjugation_4, has_correct_conjugation_5,
                                                      has_correct_conjugation_6):
    """
    Checks that /api/conjugation-game returns 200 Ok when a valid verb and conjugation is specified. The result, the
    correct answer and None as current score are returned in the request body.
    """
    random_conjugation = random.choice(conjugations)
    is_correct = has_correct_conjugation_1 and has_correct_conjugation_2 and has_correct_conjugation_3 \
                 and has_correct_conjugation_4 and has_correct_conjugation_5 and has_correct_conjugation_6

    response = api_client.post(BASE_URL, data={
        "word_id": random_conjugation.word_id,
        "tense": random_conjugation.tense,
        "conjugation_1": random_conjugation.conjugation_1 if has_correct_conjugation_1 else get_random_string(8),
        "conjugation_2": random_conjugation.conjugation_2 if has_correct_conjugation_2 else get_random_string(8),
        "conjugation_3": random_conjugation.conjugation_3 if has_correct_conjugation_3 else get_random_string(8),
        "conjugation_4": random_conjugation.conjugation_4 if has_correct_conjugation_4 else get_random_string(8),
        "conjugation_5": random_conjugation.conjugation_5 if has_correct_conjugation_5 else get_random_string(8),
        "conjugation_6": random_conjugation.conjugation_6 if has_correct_conjugation_6 else get_random_string(8)
    })

    response_body = response.data

    expected_correct_answer = get_correct_answer(random_conjugation)

    assert response.status_code == status.HTTP_200_OK
    assert response_body.get("result") is is_correct
    assert response_body.get("correct_answer") == expected_correct_answer
    assert response_body.get("score") is None


@pytest.mark.parametrize("has_correct_conjugation_1", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_2", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_3", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_4", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_5", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_6", [True, False])
@pytest.mark.django_db
def test_conjugation_game_play_authenticated_user_without_game_round(api_client, account, verbs, conjugations,
                                                                     has_correct_conjugation_1,
                                                                     has_correct_conjugation_2,
                                                                     has_correct_conjugation_3,
                                                                     has_correct_conjugation_4,
                                                                     has_correct_conjugation_5,
                                                                     has_correct_conjugation_6):
    """
    Checks that /api/conjugation-game returns 403 Forbidden when no GET request was performed previously to get a verb
    and a conjugation, and consequently persist game round data.
    """
    user, password = account()[0]

    random_conjugation = random.choice(conjugations)

    token = get_user_token(api_client, user, password)

    response = api_client.post(BASE_URL, data={
        "word_id": random_conjugation.word.id,
        "tense": random_conjugation.tense,
        "conjugation_1": random_conjugation.conjugation_1 if has_correct_conjugation_1 else get_random_string(8),
        "conjugation_2": random_conjugation.conjugation_2 if has_correct_conjugation_2 else get_random_string(8),
        "conjugation_3": random_conjugation.conjugation_3 if has_correct_conjugation_3 else get_random_string(8),
        "conjugation_4": random_conjugation.conjugation_4 if has_correct_conjugation_4 else get_random_string(8),
        "conjugation_5": random_conjugation.conjugation_5 if has_correct_conjugation_5 else get_random_string(8),
        "conjugation_6": random_conjugation.conjugation_6 if has_correct_conjugation_6 else get_random_string(8)
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("has_correct_conjugation_1", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_2", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_3", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_4", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_5", [True, False])
@pytest.mark.parametrize("has_correct_conjugation_6", [True, False])
@pytest.mark.django_db
def test_conjugation_game_play_authenticated_user(api_client, account, verbs, conjugations,
                                                  has_correct_conjugation_1, has_correct_conjugation_2,
                                                  has_correct_conjugation_3, has_correct_conjugation_4,
                                                  has_correct_conjugation_5, has_correct_conjugation_6):
    """
    Checks that /api/conjugation-game returns 200 Ok when a valid verb and conjugation is specified. The result, the
    correct answer and the current score are returned in the request body.
    """
    user, password = account()[0]
    conjugation_game = Game.objects.get(id=3)

    random_conjugation = random.choice(conjugations)
    is_correct = has_correct_conjugation_1 and has_correct_conjugation_2 and has_correct_conjugation_3 \
                 and has_correct_conjugation_4 and has_correct_conjugation_5 and has_correct_conjugation_6

    GameRound.objects.create(
        game=conjugation_game,
        user=user,
        round_data={
            "word_id": random_conjugation.word_id,
            "tense": random_conjugation.tense
        }
    )

    token = get_user_token(api_client, user, password)

    response = api_client.post(BASE_URL, data={
        "word_id": random_conjugation.word_id,
        "tense": random_conjugation.tense,
        "conjugation_1": random_conjugation.conjugation_1 if has_correct_conjugation_1 else get_random_string(8),
        "conjugation_2": random_conjugation.conjugation_2 if has_correct_conjugation_2 else get_random_string(8),
        "conjugation_3": random_conjugation.conjugation_3 if has_correct_conjugation_3 else get_random_string(8),
        "conjugation_4": random_conjugation.conjugation_4 if has_correct_conjugation_4 else get_random_string(8),
        "conjugation_5": random_conjugation.conjugation_5 if has_correct_conjugation_5 else get_random_string(8),
        "conjugation_6": random_conjugation.conjugation_6 if has_correct_conjugation_6 else get_random_string(8)
    }, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    expected_correct_answer = get_correct_answer(random_conjugation)

    assert response.status_code == status.HTTP_200_OK
    assert response_body.get("result") is is_correct
    assert response_body.get("correct_answer") == expected_correct_answer

    if is_correct:
        assert Score.objects.filter(
            user=user,
            language=random_conjugation.word.language,
            game=conjugation_game,
            score=1
        ).exists()
        assert response_body.get("score") == 1
    else:
        assert response_body.get("score") is None

    assert not GameRound.objects.filter(
        game=conjugation_game,
        user=user
    ).exists()
