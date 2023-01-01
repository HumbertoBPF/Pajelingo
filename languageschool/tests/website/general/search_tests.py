import random

import pytest
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status

from languageschool.models import Word, Meaning, Language


@pytest.mark.django_db
@pytest.mark.parametrize("all_languages", [True, False])
def test_search(client, words, all_languages):
    url = reverse('search-done')
    search_pattern = get_random_string(1)
    number_languages = Language.objects.count()
    data = {
        "search": search_pattern
    }

    k = number_languages if all_languages else random.randint(1, number_languages)
    languages = random.sample(list(Language.objects.all()), k)
    for language in languages:
        data[language.language_name] = "True"

    response = client.get(url, data=data)
    assert response.status_code == status.HTTP_200_OK
    # assert response.context.get("search") == search_pattern
    assert len(response.context.get("search_results")) <= 12
    search_results = response.context.get("search_results")

    dict_search_results = {}
    queryset_search_results = Word.objects.filter(word_name__icontains=search_pattern, language__in=languages).order_by(Lower('word_name'))

    for i in range(len(queryset_search_results)):
        dict_search_results[queryset_search_results[i]] = i

    for i in range(len(search_results)):
        assert dict_search_results.get(search_results[i]) == i


@pytest.mark.django_db
def test_dictionary(client, words, meanings):
    word = random.choice(words)
    url = reverse('meaning', kwargs={"word_id": word.id})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get('meanings'), Meaning.objects.filter(word__id=word.id), ordered=False)
