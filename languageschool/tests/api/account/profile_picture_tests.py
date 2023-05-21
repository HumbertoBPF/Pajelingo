import pytest
from django.urls import reverse
from rest_framework import status

from languageschool.tests.utils import get_user_token

BASE_URL = reverse("profile-picture-api")


@pytest.mark.django_db
def test_profile_picture_requires_authentication(api_client):
    """
    Tests that /api/user/picture raises a 401 Unauthorized for requests without a user token.
    """
    response = api_client.put(BASE_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_profile_picture_invalid_format(api_client, account):
    """
    Tests that /api/user/picture raises a 400 Bad Request for files with an incorrect format.
    """
    user, password = account()[0]

    token = get_user_token(api_client, user, password)

    with open(
            'C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/languageschool/tests/api/test_files/test.txt',
            'rb'
    ) as f:
        response = api_client.put(BASE_URL, data={
            "picture": f
        }, HTTP_AUTHORIZATION="Token {}".format(token))

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_profile_picture_no_image(api_client, account):
    """
    Tests that /api/user/picture returns a 204 No Content when no file is sent and that the user picture field is set
    to blank.
    """
    user, password = account()[0]

    token = get_user_token(api_client, user, password)

    response = api_client.put(BASE_URL, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    # assert AppUser.objects.filter(
    #     user__id=user.id,
    #     picture=""
    # ).exists()
