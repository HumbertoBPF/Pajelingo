import random

import pytest
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status

from languageschool.models import Word, Meaning


@pytest.mark.django_db
def test_search(client, words):
    url = reverse('search')
    search_pattern = get_random_string(1)
    data = {
        "search": search_pattern
    }

    response = client.get(url, data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.context.get("search") == search_pattern
    assert len(response.context.get("search_results")) <= 12
    search_results = response.context.get("search_results")

    dict_search_results = {}
    queryset_search_results = Word.objects.filter(word_name__icontains=search_pattern).order_by(Lower('word_name'))

    for i in range(len(queryset_search_results)):
        dict_search_results[queryset_search_results[i]] = i

    for i in range(len(search_results)):
        assert dict_search_results.get(search_results[i]) == i


@pytest.mark.django_db
def test_dictionary(client, words, meanings):
    word = random.choice(words)
    url = reverse('dictionary', kwargs={"word_id": word.id})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get('meanings'), Meaning.objects.filter(word__id=word.id), ordered=False)
