import base64
import random
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_get_games(api_client, games):
    url = reverse("games-api")
    response = api_client.get(url)

    returned_games = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(returned_games) == len(games)

    for i in range(len(games)):
        assert returned_games[i].get("id") is not None
        assert returned_games[i].get("game_name") is not None
        assert returned_games[i].get("android_game_activity") is not None
        assert returned_games[i].get("instructions") is not None
        assert returned_games[i].get("link") is not None
        assert games[i].id == returned_games[i].get("id")
        assert games[i].game_name == returned_games[i].get("game_name")
        assert games[i].android_game_activity == returned_games[i].get("android_game_activity")
        assert games[i].instructions == returned_games[i].get("instructions")
        assert games[i].link == returned_games[i].get("link")


@pytest.mark.django_db
def test_get_languages(api_client, languages):
    url = reverse("languages-api")
    response = api_client.get(url)

    returned_languages = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(returned_languages) == len(languages)

    for i in range(len(languages)):
        assert languages[i].id == returned_languages[i].get("id")
        assert languages[i].language_name == returned_languages[i].get("language_name")
        assert languages[i].personal_pronoun_1 == returned_languages[i].get("personal_pronoun_1")
        assert languages[i].personal_pronoun_2 == returned_languages[i].get("personal_pronoun_2")
        assert languages[i].personal_pronoun_3 == returned_languages[i].get("personal_pronoun_3")
        assert languages[i].personal_pronoun_4 == returned_languages[i].get("personal_pronoun_4")
        assert languages[i].personal_pronoun_5 == returned_languages[i].get("personal_pronoun_5")
        assert languages[i].personal_pronoun_6 == returned_languages[i].get("personal_pronoun_6")
        expected_image = None
        expected_image_url = None
        if languages[i].flag_image:
            img = languages[i].flag_image.open("rb")
            expected_image = base64.b64encode(img.read())
            expected_image_url = languages[i].flag_image.url
        assert expected_image == returned_languages[i].get("flag_image")
        assert expected_image_url == returned_languages[i].get("flag_image_uri")


@pytest.mark.django_db
def test_get_categories(api_client, categories):
    url = reverse("categories-api")
    response = api_client.get(url)

    returned_categories = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(returned_categories) == len(categories)

    for i in range(len(categories)):
        assert categories[i].id == returned_categories[i].get("id")
        assert categories[i].category_name == returned_categories[i].get("category_name")


@pytest.mark.django_db
def test_get_articles(api_client, articles):
    url = reverse("articles-api")
    response = api_client.get(url)

    returned_articles = response.data

    assert response.status_code == status.HTTP_200_OK
    assert  len(returned_articles) == len(articles)

    for i in range(len(articles)):
        assert articles[i].id == returned_articles[i].get("id")
        assert articles[i].article_name == returned_articles[i].get("article_name")
        assert articles[i].language.language_name == returned_articles[i].get("language")


@pytest.mark.django_db
def test_get_words(api_client, words):
    url = reverse("words-api")
    response = api_client.get(url)

    returned_words = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(returned_words) == len(words)

    for i in range(len(words)):
        assert words[i].id == returned_words[i].get("id")
        assert words[i].word_name == returned_words[i].get("word_name")
        assert words[i].language.language_name == returned_words[i].get("language")
        assert words[i].article.id == returned_words[i].get("article")
        expected_category = None if (words[i].category is None) else words[i].category.category_name
        assert expected_category == returned_words[i].get("category")
        assert list(words[i].synonyms.all().values_list('id', flat=True)) == returned_words[i].get("synonyms")
        expected_image_url = words[i].image.url if words[i].image else None
        assert expected_image_url == returned_words[i].get("image")
        assert returned_words[i].get("is_favorite") is None


@pytest.mark.django_db
def test_get_meanings(api_client, meanings):
    url = reverse("meanings-api")
    response = api_client.get(url)

    returned_meanings = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(meanings) == len(returned_meanings)

    for i in range(len(meanings)):
        assert meanings[i].id == returned_meanings[i].get("id")
        assert meanings[i].word.id == returned_meanings[i].get("word")
        assert meanings[i].meaning == returned_meanings[i].get("meaning")


@pytest.mark.django_db
def test_get_conjugations(api_client, conjugations):
    url = reverse("conjugations-api")
    response = api_client.get(url)

    returned_conjugations = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(conjugations) == len(returned_conjugations)

    for i in range(len(conjugations)):
        assert conjugations[i].id == returned_conjugations[i].get("id")
        assert conjugations[i].word.id == returned_conjugations[i].get("word")
        assert conjugations[i].conjugation_1 == returned_conjugations[i].get("conjugation_1")
        assert conjugations[i].conjugation_2 == returned_conjugations[i].get("conjugation_2")
        assert conjugations[i].conjugation_3 == returned_conjugations[i].get("conjugation_3")
        assert conjugations[i].conjugation_4 == returned_conjugations[i].get("conjugation_4")
        assert conjugations[i].conjugation_5 == returned_conjugations[i].get("conjugation_5")
        assert conjugations[i].conjugation_6 == returned_conjugations[i].get("conjugation_6")
        assert conjugations[i].tense == returned_conjugations[i].get("tense")


@pytest.mark.parametrize("has_language_filter", [True, False])
@pytest.mark.parametrize("has_user_filter", [True, False])
@pytest.mark.django_db
def test_get_scores(api_client, account, games, languages, score, has_language_filter, has_user_filter):
    accounts = account(n=random.randint(20, 50))

    users = []

    for account in accounts:
        user, _ = account
        users.append(user)

    scores = score(users=users, games=games, languages=languages)

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

    returned_scores = response.data

    assert response.status_code == status.HTTP_200_OK
    assert len(scores) == len(returned_scores)

    for i in range(len(scores)):
        assert scores[i].id == returned_scores[i].get("id")
        assert scores[i].user.username == returned_scores[i].get("user")
        assert scores[i].language.language_name == returned_scores[i].get("language")
        assert scores[i].game.game_name == returned_scores[i].get("game")
