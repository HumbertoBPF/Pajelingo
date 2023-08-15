import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.tests.utils import attribute_user_badges, get_user_token, assert_badges, get_profile_picture_base64

URL = reverse("user-api")


@pytest.mark.django_db
def test_account_get_requires_authentication(api_client):
    """
    Tests that the GET /user endpoint requires token authentication.
    """
    response = api_client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_get_wrong_token(api_client):
    """
    Tests that the GET /user endpoint returns 401 Unauthorized when an invalid token is used.
    """
    response = api_client.get(URL, HTTP_AUTHORIZATION="Token {}".format(get_random_string(16)))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_get(api_client, account, badges):
    """
    Tests that the GET /user endpoint returns 200 when the credentials are correct.
    """
    user, password = account()[0]
    attribute_user_badges()

    token = get_user_token(api_client, user, password)

    response = api_client.get(URL, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_200_OK
    # Checking the response body
    response_body = response.data
    assert response_body.get("username") == user.username
    assert response_body.get("email") == user.email
    assert response_body.get("bio") is not None
    assert response_body.get("picture") == get_profile_picture_base64(user)
    assert len(response_body.get("badges")) == 2
    assert_badges(response_body.get("badges"), user)
    # Checks that no password is returned
    assert response_body.get("password") is None