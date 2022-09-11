import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status

from languageschool.models import Score


def generate_answer_conjugation_game(client, conjugation, is_correct_answer):
    url = reverse("conjugation-game-verify-answer")

    form_data = {
        "conjugation_1": conjugation.conjugation_1 if is_correct_answer else get_random_string(random.randint(1, 30)),
        "conjugation_2": conjugation.conjugation_2 if is_correct_answer else get_random_string(random.randint(1, 30)),
        "conjugation_3": conjugation.conjugation_3 if is_correct_answer else get_random_string(random.randint(1, 30)),
        "conjugation_4": conjugation.conjugation_4 if is_correct_answer else get_random_string(random.randint(1, 30)),
        "conjugation_5": conjugation.conjugation_5 if is_correct_answer else get_random_string(random.randint(1, 30)),
        "conjugation_6": conjugation.conjugation_6 if is_correct_answer else get_random_string(random.randint(1, 30)),
        "word_id": conjugation.word.id,
        "tense": conjugation.tense
    }

    response = client.post(url, data=form_data)

    assert response.status_code == status.HTTP_302_FOUND
    base_url = reverse('conjugation-game')
    query_string = urlencode({'language': str(conjugation.word.language)})
    url = '{}?{}'.format(base_url, query_string)
    assert response.url == url


@pytest.mark.django_db
def test_conjugation_game_setup_page(client, languages):
    url = reverse('conjugation-game-setup')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get("languages"), languages, ordered=False)


@pytest.mark.parametrize(
    "language", [
        None,
        ""
    ]
)
@pytest.mark.django_db
def test_conjugation_game_setup_no_language_selected(client, languages, language):
    url = reverse('conjugation-game')
    form_data = {}

    if language is not None:
        form_data["language"] = language

    response = client.get(url, data=form_data)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('conjugation-game-setup')


@pytest.mark.django_db
def test_conjugation_game_setup_invalid_languages(client, languages):
    url = reverse('conjugation-game')
    form_data = {"language": get_random_string(random.randint(1, 30))}

    response = client.get(url, data=form_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "index_language", range(5)
)
@pytest.mark.django_db
def test_conjugation_game_setup(client, languages, verbs, conjugations, index_language):
    url = reverse('conjugation-game')
    form_data = {
        "language": languages[index_language].language_name
    }

    response = client.get(url, data=form_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.context.get("word") is not None
    assert response.context.get("tense") is not None


@pytest.mark.parametrize(
    "is_correct_answer", [
        True, False
    ]
)
@pytest.mark.django_db
def test_conjugation_game_answer(client, conjugations, conjugation_game, is_correct_answer):
    conjugation = random.choice(conjugations)
    generate_answer_conjugation_game(client, conjugation, is_correct_answer)


@pytest.mark.parametrize(
    "is_correct_answer", [
        True, False
    ]
)
@pytest.mark.django_db
def test_conjugation_game_answer_authenticated_user_first_play(client, account, conjugations, conjugation_game, is_correct_answer):
    user, password = account
    client.login(username=user.username, password=password)

    conjugation = random.choice(conjugations)
    target_language = conjugation.word.language

    generate_answer_conjugation_game(client, conjugation, is_correct_answer)

    if is_correct_answer:
        assert Score.objects.filter(user=user, game=conjugation_game, language=target_language, score=1).exists()
    else:
        assert not Score.objects.filter(user=user, game=conjugation_game, language=target_language).exists()


@pytest.mark.parametrize(
    "is_correct_answer", [
        True, False
    ]
)
@pytest.mark.django_db
def test_conjugation_game_answer_authenticated_user(client, account, conjugations, conjugation_game, score, is_correct_answer):
    user, password = account
    client.login(username=user.username, password=password)

    conjugation = random.choice(conjugations)
    initial_score = random.randint(100, 1000)
    target_language = conjugation.word.language

    score(user=user, games=[conjugation_game], languages=[target_language], initial_score=initial_score)

    generate_answer_conjugation_game(client, conjugation, is_correct_answer)

    if is_correct_answer:
        assert Score.objects.filter(user=user, game=conjugation_game,
                                    language=target_language, score=initial_score+1).exists()
    else:
        assert Score.objects.filter(user=user, game=conjugation_game,
                                    language=target_language, score=initial_score).exists()


@pytest.mark.django_db
def test_conjugation_game_verb_not_found(client, conjugations, conjugation_game):
    url = reverse("conjugation-game-verify-answer")
    conjugation = random.choice(conjugations)

    form_data = {
        "conjugation_1": conjugation.conjugation_1,
        "conjugation_2": conjugation.conjugation_2,
        "conjugation_3": conjugation.conjugation_3,
        "conjugation_4": conjugation.conjugation_4,
        "conjugation_5": conjugation.conjugation_5,
        "conjugation_6": conjugation.conjugation_6,
        "word_id": random.randint(100, 1000),
        "tense": conjugation.tense
    }

    response = client.post(url, data=form_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_conjugation_game_tense_not_found(client, conjugations, conjugation_game):
    url = reverse("conjugation-game-verify-answer")
    conjugation = random.choice(conjugations)

    form_data = {
        "conjugation_1": conjugation.conjugation_1,
        "conjugation_2": conjugation.conjugation_2,
        "conjugation_3": conjugation.conjugation_3,
        "conjugation_4": conjugation.conjugation_4,
        "conjugation_5": conjugation.conjugation_5,
        "conjugation_6": conjugation.conjugation_6,
        "word_id": conjugation.word.id,
        "tense": get_random_string(random.randint(1, 30))
    }

    response = client.post(url, data=form_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
