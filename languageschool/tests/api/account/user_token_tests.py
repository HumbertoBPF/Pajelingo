import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

URL = reverse("user-token-api")


@pytest.mark.parametrize("has_username, has_password", [
    (True, False),
    (False, True),
    (False, False)
])
@pytest.mark.django_db
def test_user_token_required_parameters(api_client, account, has_username, has_password):
    """
    Tests that /api/user-token raises 400 Bad Request when some required parameter is missing.
    """
    user, password = account()[0]
    payload ={}

    if has_username:
        payload["username"] = user.username

    if has_password:
        payload["password"] = password

    response = api_client.post(URL, data=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("has_valid_username, has_valid_password", [
    (True, False),
    (False, True),
    (False, False)
])
@pytest.mark.django_db
def test_user_token_invalid_credentials(api_client, account, has_valid_username, has_valid_password):
    """
    Tests that /api/user-token raises 400 Bad Request when the authentication fails.
    """
    user, password = account()[0]

    response = api_client.post(URL, data={
        "username": user.username if has_valid_username else get_random_string(8),
        "password": password if has_valid_password else get_random_string(8)
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_token(api_client, account):
    """
    Tests that /api/user-token returns the user token when the authentication is successful.
    """
    user, password = account()[0]

    response = api_client.post(URL, data={
        "username": user.username,
        "password": password
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("token") is not None
