import base64
import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from rest_framework import status

from languageschool.models import Game
from languageschool.tests.utils import get_users


@pytest.mark.django_db
def test_get_games(api_client):
    number_games = Game.objects.count()

    url = reverse("games-api")
    response = api_client.get(url)

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(response_body) == number_games

    for i in range(number_games):
        pk = response_body[i].get("id")
        game_name = response_body[i].get("game_name")
        android_game_activity = response_body[i].get("android_game_activity")
        instructions = response_body[i].get("instructions")
        link = response_body[i].get("link")
        assert Game.objects.filter(
            id=pk,
            game_name=game_name,
            android_game_activity=android_game_activity,
            instructions=instructions,
            link=link
        ).exists()


@pytest.mark.django_db
def test_get_languages(api_client, languages):
    number_languages = languages.count()

    url = reverse("languages-api")
    response = api_client.get(url)

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(response_body) == number_languages

    for i in range(number_languages):
        assert languages[i].id == response_body[i].get("id")
        assert languages[i].language_name == response_body[i].get("language_name")
        assert languages[i].personal_pronoun_1 == response_body[i].get("personal_pronoun_1")
        assert languages[i].personal_pronoun_2 == response_body[i].get("personal_pronoun_2")
        assert languages[i].personal_pronoun_3 == response_body[i].get("personal_pronoun_3")
        assert languages[i].personal_pronoun_4 == response_body[i].get("personal_pronoun_4")
        assert languages[i].personal_pronoun_5 == response_body[i].get("personal_pronoun_5")
        assert languages[i].personal_pronoun_6 == response_body[i].get("personal_pronoun_6")
        expected_image = None
        expected_image_url = None
        if languages[i].flag_image:
            img = languages[i].flag_image.open("rb")
            expected_image = base64.b64encode(img.read())
            expected_image_url = languages[i].flag_image.url
        assert expected_image == response_body[i].get("flag_image")
        assert expected_image_url == response_body[i].get("flag_image_uri")


@pytest.mark.django_db
def test_get_categories(api_client, categories):
    number_categories = categories.count()

    url = reverse("categories-api")
    response = api_client.get(url)

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(response_body) == number_categories

    for i in range(number_categories):
        assert categories[i].id == response_body[i].get("id")
        assert categories[i].category_name == response_body[i].get("category_name")


@pytest.mark.django_db
def test_get_articles(api_client, articles):
    number_articles = articles.count()

    url = reverse("articles-api")
    response = api_client.get(url)

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert  len(response_body) == number_articles

    for i in range(number_articles):
        assert articles[i].id == response_body[i].get("id")
        assert articles[i].article_name == response_body[i].get("article_name")
        assert articles[i].language.language_name == response_body[i].get("language")


@pytest.mark.django_db
def test_get_words(api_client, words):
    number_words = words.count()

    url = reverse("words-api")
    response = api_client.get(url)

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(response_body) == number_words

    for i in range(number_words):
        assert words[i].id == response_body[i].get("id")
        assert words[i].word_name == response_body[i].get("word_name")
        assert words[i].language.language_name == response_body[i].get("language")
        assert words[i].article_id == response_body[i].get("article")
        expected_category = None if (words[i].category is None) else words[i].category.category_name
        assert expected_category == response_body[i].get("category")
        assert list(words[i].synonyms.values_list('id', flat=True)) == response_body[i].get("synonyms")
        expected_image_url = words[i].image.url if words[i].image else None
        assert expected_image_url == response_body[i].get("image")
        assert response_body[i].get("is_favorite") is None


@pytest.mark.django_db
def test_get_meanings(api_client, meanings):
    number_meanings = meanings.count()

    url = reverse("meanings-api")
    response = api_client.get(url)

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(response_body) == number_meanings

    for i in range(number_meanings):
        assert meanings[i].id == response_body[i].get("id")
        assert meanings[i].word_id == response_body[i].get("word")
        assert meanings[i].meaning == response_body[i].get("meaning")


@pytest.mark.django_db
def test_get_conjugations(api_client, conjugations):
    number_conjugations = conjugations.count()

    url = reverse("conjugations-api")
    response = api_client.get(url)

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(response_body) == number_conjugations

    for i in range(number_conjugations):
        assert conjugations[i].id == response_body[i].get("id")
        assert conjugations[i].word_id == response_body[i].get("word")
        assert conjugations[i].conjugation_1 == response_body[i].get("conjugation_1")
        assert conjugations[i].conjugation_2 == response_body[i].get("conjugation_2")
        assert conjugations[i].conjugation_3 == response_body[i].get("conjugation_3")
        assert conjugations[i].conjugation_4 == response_body[i].get("conjugation_4")
        assert conjugations[i].conjugation_5 == response_body[i].get("conjugation_5")
        assert conjugations[i].conjugation_6 == response_body[i].get("conjugation_6")
        assert conjugations[i].tense == response_body[i].get("tense")


@pytest.mark.parametrize("has_language_filter", [True, False])
@pytest.mark.parametrize("has_user_filter", [True, False])
@pytest.mark.django_db
def test_get_scores(api_client, account, languages, score, has_language_filter, has_user_filter):
    accounts = account(n=random.randint(20, 50))

    users = get_users(accounts)

    scores = score(users=users, languages=languages)

    url_params = {}

    if has_language_filter:
        random_language = random.choice(languages)
        url_params["language"] = random_language.language_name
        scores = scores.filter(language=random_language)

    if has_user_filter:
        random_user = random.choice(users)
        url_params["user"] = random_user.username
        scores = scores.filter(user=random_user)

    base_url = reverse("scores-api")
    query_string = urlencode(url_params)
    url = "{}?{}".format(base_url, query_string)
    response = api_client.get(url)

    response_body = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(scores) == len(response_body)

    for i in range(len(scores)):
        assert scores[i].id == response_body[i].get("id")
        assert scores[i].user.username == response_body[i].get("user")
        assert scores[i].language.language_name == response_body[i].get("language")
        assert scores[i].game.game_name == response_body[i].get("game")
