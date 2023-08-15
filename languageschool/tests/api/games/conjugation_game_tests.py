import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import Conjugation, Score, GameRound, Badge
from languageschool.tests.utils import get_user_token, get_conjugation_game_answer, achieve_explorer_badge

CONJUGATION_GAME_URL = reverse("conjugation-game-api")


@pytest.mark.django_db
def test_conjugation_game_setup_no_language(api_client):
    """
    Checks that /api/conjugation-game raises a 404 Not Found when no language is specified.
    """
    response = api_client.get(CONJUGATION_GAME_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_conjugation_game_setup_invalid_language(api_client):
    """
    Checks that /api/conjugation-game raises a 404 Not Found when a invalid language is specified.
    """
    query_string = urlencode({
        "language": get_random_string(8)
    })
    url = "{}?{}".format(CONJUGATION_GAME_URL, query_string)

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
    url = "{}?{}".format(CONJUGATION_GAME_URL, query_string)

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
    url = "{}?{}".format(CONJUGATION_GAME_URL, query_string)

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


@pytest.mark.parametrize(
    "field", [
        "word_id",
        "tense",
        "conjugation_1",
        "conjugation_2",
        "conjugation_3",
        "conjugation_4",
        "conjugation_5",
        "conjugation_6"
    ]
)
@pytest.mark.django_db
def test_conjugation_game_play_required_parameters(api_client, field):
    """
    Checks that /api/conjugation-game returns 400 Bad Request when some required parameter is missing.
    """
    payload = {
        "word_id": random.randint(1, 1000),
        "tense":get_random_string(8),
        "conjugation_1": get_random_string(8),
        "conjugation_2": get_random_string(8),
        "conjugation_3": get_random_string(8),
        "conjugation_4": get_random_string(8),
        "conjugation_5": get_random_string(8),
        "conjugation_6": get_random_string(8)
    }

    del payload[field]

    response = api_client.post(CONJUGATION_GAME_URL, data=payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body[field]) == 1
    assert str(response_body[field][0]) == "This field is required."


@pytest.mark.django_db
def test_conjugation_game_play_invalid_verb(api_client):
    """
    Checks that /api/conjugation-game raises a 404 Not Found when the specified word id does not match any verb.
    """
    response = api_client.post(CONJUGATION_GAME_URL, data={
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

    response = api_client.post(CONJUGATION_GAME_URL, data={
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
def test_conjugation_game_play_non_authenticated_user(api_client, account, verbs, conjugations,
                                                      has_correct_conjugation_1, has_correct_conjugation_2,
                                                      has_correct_conjugation_3, has_correct_conjugation_4,
                                                      has_correct_conjugation_5, has_correct_conjugation_6):
    """
    Checks that /api/conjugation-game returns 200 Ok when a valid verb and conjugation is specified. The result, the
    correct answer and None as current score are returned in the request body.
    """
    user, _ = account()[0]
    achieve_explorer_badge(user)

    random_conjugation = random.choice(conjugations)
    is_correct = has_correct_conjugation_1 and has_correct_conjugation_2 and has_correct_conjugation_3 \
                 and has_correct_conjugation_4 and has_correct_conjugation_5 and has_correct_conjugation_6

    response = api_client.post(CONJUGATION_GAME_URL, data={
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

    expected_correct_answer = get_conjugation_game_answer(random_conjugation)

    assert response.status_code == status.HTTP_200_OK
    assert response_body.get("result") is is_correct
    assert response_body.get("correct_answer") == expected_correct_answer
    assert response_body.get("score") is None
    assert response_body.get("new_badges") == []


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

    response = api_client.post(CONJUGATION_GAME_URL, data={
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
    achieve_explorer_badge(user)

    conjugation_game_id = 3

    random_conjugation = random.choice(conjugations)
    is_correct = has_correct_conjugation_1 and has_correct_conjugation_2 and has_correct_conjugation_3 \
                 and has_correct_conjugation_4 and has_correct_conjugation_5 and has_correct_conjugation_6

    initial_score = Score.objects.filter(
        user=user,
        language=random_conjugation.word.language,
        game__id=conjugation_game_id
    ).first()

    GameRound.objects.create(
        game_id=conjugation_game_id,
        user=user,
        round_data={
            "word_id": random_conjugation.word_id,
            "tense": random_conjugation.tense
        }
    )

    token = get_user_token(api_client, user, password)

    response = api_client.post(CONJUGATION_GAME_URL, data={
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

    expected_correct_answer = get_conjugation_game_answer(random_conjugation)

    assert response.status_code == status.HTTP_200_OK
    assert response_body.get("result") is is_correct
    assert response_body.get("correct_answer") == expected_correct_answer

    if is_correct:
        expected_score = 1 if (initial_score is None) else initial_score.score + 1

        assert Score.objects.filter(
            user=user,
            language=random_conjugation.word.language,
            game_id=conjugation_game_id,
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
        game_id=conjugation_game_id,
        user=user
    ).exists()
