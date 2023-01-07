import pytest
from django.urls import reverse
from rest_framework import status

from languageschool.tests.api.comparers import SimpleComparer, ArticleComparer, MeaningComparer, ConjugationComparer, \
    WordComparer, ListScoresComparer, LanguageComparer
from languageschool.tests.utils import deserialize_data, is_model_objects_equal_to_dict_array


@pytest.mark.django_db
def test_game_endpoint(api_client, games):
    url = reverse("games-api")
    response = api_client.get(url)

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(games, data, SimpleComparer())


@pytest.mark.django_db
def test_language_endpoint(api_client, languages):
    url = reverse("languages-api")
    response = api_client.get(url)

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(languages, data, LanguageComparer())


@pytest.mark.django_db
def test_categories_endpoint(api_client, categories):
    url = reverse("categories-api")
    response = api_client.get(url)

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(categories, data, SimpleComparer())


@pytest.mark.django_db
def test_articles_endpoint(api_client, articles):
    url = reverse("articles-api")
    response = api_client.get(url)

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(articles, data, ArticleComparer())


@pytest.mark.django_db
def test_words_endpoint(api_client, words):
    url = reverse("words-api")
    response = api_client.get(url)

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(words, data, WordComparer())


@pytest.mark.django_db
def test_meanings_endpoint(api_client, meanings):
    url = reverse("meanings-api")
    response = api_client.get(url)

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(meanings, data, MeaningComparer())


@pytest.mark.django_db
def test_conjugations_endpoint(api_client, conjugations):
    url = reverse("conjugations-api")
    response = api_client.get(url)

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(conjugations, data, ConjugationComparer())


@pytest.mark.django_db
def test_conjugations_endpoint(api_client, account, games, languages, score):
    user, password = account()[0]
    scores = score(users=[user], games=games, languages=languages)

    url = reverse("scores-api")
    response = api_client.get(url)

    data = deserialize_data(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert is_model_objects_equal_to_dict_array(scores, data, ListScoresComparer())
