import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status

from languageschool.models import Score


def generate_answer_vocabulary_game(client, word_to_translate, languages, is_correct_answer):
    url = reverse("vocabulary-game-verify-answer")

    if is_correct_answer:
        translation_word = random.choice(word_to_translate.synonyms.all())
        base_language = translation_word.language
        form_data = {
            "word_to_translate_id": word_to_translate.id,
            "translation_word": translation_word.word_name,
            "base_language": base_language.language_name
        }
    else:
        translation_word = get_random_string(random.randint(1, 30))
        base_language = random.choice(languages)
        form_data = {
            "word_to_translate_id": word_to_translate.id,
            "translation_word": translation_word,
            "base_language": base_language.language_name
        }

    response = client.post(url, data=form_data)

    assert response.status_code == status.HTTP_302_FOUND
    base_url = reverse('vocabulary-game')
    query_string = urlencode({'base_language': str(base_language),
                              'target_language': str(word_to_translate.language)})
    url = "{}?{}".format(base_url, query_string)
    assert response.url == url


@pytest.mark.django_db
def test_vocabulary_game_setup_page(client, languages):
    url = reverse('vocabulary-game-setup')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get("languages"), languages, ordered=False)


@pytest.mark.parametrize(
    "base_language", [
        None,
        ""
    ]
)
@pytest.mark.parametrize(
    "target_language", [
        None,
        ""
    ]
)
@pytest.mark.django_db
def test_vocabulary_game_setup_no_language_selected(client, languages, base_language, target_language):
    url = reverse('vocabulary-game')
    form_data = {}

    if base_language is not None:
        form_data["base_language"] = base_language
    if target_language is not None:
        form_data["target_language"] = target_language

    response = client.get(url, data=form_data)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('vocabulary-game-setup')


@pytest.mark.django_db
def test_vocabulary_game_setup_invalid_or_equal_languages(client, languages):
    url = reverse('vocabulary-game')
    form_data = {
        "base_language": get_random_string(random.randint(1, 30)),
        "target_language": get_random_string(random.randint(1, 30))
    }

    response = client.get(url, data=form_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "index_base_language", range(5)
)
@pytest.mark.parametrize(
    "index_target_language", range(5)
)
@pytest.mark.django_db
def test_vocabulary_game_setup(client, languages, words, index_base_language, index_target_language):
    url = reverse('vocabulary-game')
    form_data = {
        "base_language": languages[index_base_language].language_name,
        "target_language": languages[index_target_language].language_name
    }

    response = client.get(url, data=form_data)

    if index_base_language != index_target_language:
        assert response.status_code == status.HTTP_200_OK
        assert response.context.get("base_language") is not None
        assert response.context.get("word") is not None
    else:
        assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.parametrize(
    "is_correct_answer", [True, False]
)
@pytest.mark.django_db
def test_vocabulary_game_answer(client, languages, words, vocabulary_game, is_correct_answer):
    word_to_translate = random.choice(words)
    generate_answer_vocabulary_game(client, word_to_translate, languages, is_correct_answer)


@pytest.mark.parametrize(
    "is_correct_answer", [True, False]
)
@pytest.mark.django_db
def test_vocabulary_game_answer_user_authenticated_first_play(client, account, languages, words, vocabulary_game, is_correct_answer):
    user, password = account
    client.login(username=user.username, password=password)

    word_to_translate = random.choice(words)
    target_language = word_to_translate.language

    generate_answer_vocabulary_game(client, word_to_translate, languages, is_correct_answer)

    if is_correct_answer:
        assert Score.objects.filter(user=user, game=vocabulary_game,
                                    language=target_language, score=1).first() is not None
    else:
        assert Score.objects.filter(user=user, game=vocabulary_game, language=target_language).first() is None


@pytest.mark.parametrize(
    "is_correct_answer", [True, False]
)
@pytest.mark.django_db
def test_vocabulary_game_answer_user_authenticated(client, account, languages, words, vocabulary_game, score, is_correct_answer):
    user, password = account
    initial_score = random.randint(100, 1000)

    client.login(username=user.username, password=password)

    word_to_translate = random.choice(words)
    target_language = word_to_translate.language
    score(user=user, game=vocabulary_game, language=target_language, initial_score=initial_score)

    generate_answer_vocabulary_game(client, word_to_translate, languages, is_correct_answer)

    if is_correct_answer:
        assert Score.objects.filter(user=user, game=vocabulary_game, language=target_language,
                                    score=initial_score + 1).first() is not None
    else:
        assert Score.objects.filter(user=user, game=vocabulary_game, language=target_language,
                                    score=initial_score).first() is not None


@pytest.mark.django_db
def test_vocabulary_game_not_found_base_language(client, languages, words, vocabulary_game):
    url = reverse("vocabulary-game-verify-answer")
    form_data = {
        "word_to_translate_id": random.choice(words).id,
        "base_language": get_random_string(random.randint(1, 30)),
        "translation_word": get_random_string(random.randint(1, 30))
    }

    response = client.post(url, data=form_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_vocabulary_game_not_found_word_to_translate(client, languages, words, vocabulary_game):
    url = reverse("vocabulary-game-verify-answer")
    form_data = {
        "word_to_translate_id": random.randint(100, 30000),
        "base_language": random.choice(languages).language_name,
        "translation_word": get_random_string(random.randint(1, 30))
    }

    response = client.post(url, data=form_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
