import random

import pytest
from django.urls import reverse
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status


@pytest.mark.django_db
def test_rankings(client, account, games, languages, score):
    accounts = account(n=random.randint(5, 30))

    users = []

    for user, password in accounts:
        users.append(user)

    score(users=users, games=games, languages=languages)

    url = reverse('rankings')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get("languages"), languages, ordered=False)
