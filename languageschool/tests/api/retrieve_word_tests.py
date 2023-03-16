import random

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_retrieve_word_not_found(api_client):
    """
    Tests that the endpoint returns 404 Not Found when the specified id does not match a word.
    """
    pk = random.randint(1, 1000)
    url = reverse("word-api", kwargs={"pk": pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_word(api_client, words):
    random_word = random.choice(words)
    url = reverse("word-api", kwargs={"pk": random_word.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    word = response.data

    assert word.get("id") == random_word.id
    assert word.get("word_name") == random_word.word_name
    assert word.get("language") == random_word.language.language_name
    assert word.get("category") == (None if (random_word.category is None) else random_word.category.category_name)
    assert word.get("article") == random_word.article.id
    assert word.get("synonyms") == list(random_word.synonyms.all().values_list("id", flat=True))
