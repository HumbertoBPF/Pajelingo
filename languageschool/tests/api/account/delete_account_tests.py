import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import User
from languageschool.tests.utils import get_user_token

URL = reverse("user-api")


@pytest.mark.django_db
def test_account_delete_requires_authentication(api_client):
    """
    Tests that the DELETE /user endpoint requires token authentication.
    """
    response = api_client.delete(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_delete_wrong_credentials(api_client):
    """
    Tests that the DELETE /user endpoint returns 401 Unauthorized when an invalid token is used.
    """
    response = api_client.delete(URL, HTTP_AUTHORIZATION="Token {}".format(get_random_string(16)))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_delete(api_client, account):
    """
    Tests the DELETE /user endpoint.
    """
    user, password = account()[0]

    token = get_user_token(api_client, user, password)

    response = api_client.delete(URL, HTTP_AUTHORIZATION="Token {}".format(token))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert User.objects.count() == 0
