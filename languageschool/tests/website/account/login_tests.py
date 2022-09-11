import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.tests.conftest import is_user_authenticated


@pytest.mark.parametrize(
    "username", [
        None,
        get_random_string(random.randint(10, 30))
    ]
)
@pytest.mark.parametrize(
    "password", [
        None,
        get_random_string(random.randint(1, 50))
    ]
)
@pytest.mark.django_db
def test_login_fail(client, account, username, password):
    user, password = account()[0]

    url = reverse('account-auth-user')
    data = {}

    if username is not None:
        data["username"] = username

    if password is not None:
        data["password"] = password

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert not is_user_authenticated(client, user)


@pytest.mark.django_db
def test_login_success(client, account):
    user, password = account()[0]

    url = reverse('account-auth-user')
    data = {
        "username": user.username,
        "password": password
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_302_FOUND
    assert is_user_authenticated(client, user)


@pytest.mark.django_db
def test_logout(client, account):
    user, password = account()[0]
    client.login(username=user.username, password=password)

    assert is_user_authenticated(client, user)

    url = reverse('account-logout')
    response = client.get(url)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('index')
    assert not is_user_authenticated(client, user)
