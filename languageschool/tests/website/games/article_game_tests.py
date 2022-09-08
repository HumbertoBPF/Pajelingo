import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status

from languageschool.models import Score


def generate_answer_article_game(client, word, is_correct_answer):
    url = reverse("article-game-verify-answer")
    form_data = {
        "article": word.article.article_name if is_correct_answer else get_random_string(random.randint(1, 10)),
        "word_id": word.id
    }

    response = client.post(url, data=form_data)

    assert response.status_code == status.HTTP_302_FOUND
    base_url = reverse('article-game')
    query_string = urlencode({'language': str(word.language)})
    url = '{}?{}'.format(base_url, query_string)
    assert response.url == url


@pytest.mark.django_db
def test_article_game_setup_page(client, languages):
    url = reverse('article-game-setup')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get("languages"), languages.exclude(language_name="English"), ordered=False)


@pytest.mark.parametrize(
    "language", [
        None,
        ""
    ]
)
@pytest.mark.django_db
def test_article_game_setup_no_language_selected(client, languages, language):
    url = reverse('article-game')
    form_data = {}

    if language is not None:
        form_data["language"] = language

    response = client.get(url, data=form_data)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('article-game-setup')


@pytest.mark.django_db
def test_article_game_setup_invalid_languages(client, languages):
    url = reverse('article-game')
    form_data = {"language": get_random_string(random.randint(1, 30))}

    response = client.get(url, data=form_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "index_language", range(5)
)
@pytest.mark.django_db
def test_article_game_setup(client, languages, words, index_language):
    url = reverse('article-game')
    language = languages[index_language].language_name
    form_data = {
        "language": language
    }

    response = client.get(url, data=form_data)

    if language != "English":
        assert response.status_code == status.HTTP_200_OK
        assert response.context.get("word") is not None
    else:
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == reverse('article-game-setup')


@pytest.mark.parametrize(
    "is_correct_answer", [
        True, False
    ]
)
@pytest.mark.django_db
def test_article_game_answer(client, words, article_game, is_correct_answer):
    word = random.choice(words)
    generate_answer_article_game(client, word, is_correct_answer)


@pytest.mark.parametrize(
    "is_correct_answer", [
        True, False
    ]
)
@pytest.mark.django_db
def test_article_game_answer_authenticated_user_first_play(client, account, words, article_game, is_correct_answer):
    user, password = account
    client.login(username=user.username, password=password)

    word = random.choice(words)
    target_language = word.language

    generate_answer_article_game(client, word, is_correct_answer)

    if is_correct_answer:
        assert Score.objects.filter(user=user, language=target_language, game=article_game, score=1).first() is not None
    else:
        assert Score.objects.filter(user=user, language=target_language, game=article_game).first() is None


@pytest.mark.parametrize(
    "is_correct_answer", [
        True, False
    ]
)
@pytest.mark.django_db
def test_article_game_answer_authenticated_user(client, account, words, article_game, score, is_correct_answer):
    user, password = account
    client.login(username=user.username, password=password)
    initial_score = random.randint(100, 1000)

    word = random.choice(words)
    target_language = word.language

    score(user=user, game=article_game, language=target_language, initial_score=initial_score)
    generate_answer_article_game(client, word, is_correct_answer)

    if is_correct_answer:
        assert Score.objects.filter(user=user, game=article_game, language=target_language, score=initial_score+1)\
                   .first() is not None
    else:
        assert Score.objects.filter(user=user, game=article_game, language=target_language, score=initial_score) \
                   .first() is not None


@pytest.mark.django_db
def test_article_game_not_found_word(client, languages, words, vocabulary_game):
    url = reverse("article-game-verify-answer")
    form_data = {
        "article": get_random_string(random.randint(1, 10)),
        "word_id": random.randint(100, 30000)
    }

    response = client.post(url, data=form_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
