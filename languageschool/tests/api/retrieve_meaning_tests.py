import random

import pytest
from django.urls import reverse
from rest_framework import status

from languageschool.models import Meaning


@pytest.mark.django_db
def test_retrieve_meaning_not_found(api_client):
    """
    Testing that if the primary key specified as path argument does not match any meaning, then a 404 Not Found is
    raised
    """
    pk = random.randint(1, 1000)
    url = reverse("meaning-api", kwargs={"pk": pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_meaning(api_client, words, meanings):
    """
    Tests that all the meanings of the specified word are returned.
    """
    random_word = random.choice(words)

    url = reverse("meaning-api", kwargs={"pk": random_word.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    returned_meanings = response.data

    for meaning in returned_meanings:
        assert Meaning.objects.filter(id=meaning.get("id"),
                                      word__id=meaning.get("word"),
                                      meaning=meaning.get("meaning")).exists()

    assert len(returned_meanings) == meanings.filter(word__id=random_word.id).count()