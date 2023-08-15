import random

import pytest
from django.core import mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import User
from languageschool.tests.utils import get_random_email, get_random_username, get_valid_password, \
    get_too_short_username, get_too_long_password, get_too_short_password, get_password_without_letters, \
    get_password_without_digits, get_password_without_special_characters, get_profile_picture_base64
from languageschool.utils import SIGN_UP_SUBJECT, SIGN_UP_MESSAGE
from pajelingo import settings

URL = reverse("user-api")


@pytest.mark.parametrize("field", ["email", "username", "password", "bio"])
@pytest.mark.django_db
def test_signup_required_params(api_client, field):
    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    del payload[field]

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body[field]) == 1
    assert str(response_body[field][0]) == "This field is required."


@pytest.mark.django_db
def test_signup_email_with_space(api_client):
    payload = {
        "email": f"{get_random_string(random.randint(1, 5))} {get_random_email()}",
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["email"]) == 1
    assert str(response_body["email"][0]) == "Enter a valid email address."


@pytest.mark.django_db
def test_signup_email_wrong_format(api_client):
    payload = {
        "email": get_random_string(random.randint(1, 16)),
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["email"]) == 1
    assert str(response_body["email"][0]) == "Enter a valid email address."


@pytest.mark.django_db
def test_signup_blank_email(api_client):
    payload = {
        "email": "",
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["email"]) == 1
    assert str(response_body["email"][0]) == "This field may not be blank."


@pytest.mark.django_db
def test_signup_username_with_space(api_client):
    payload = {
        "email": get_random_email(),
        "username": f"{get_random_string(random.randint(1, 5))} {get_random_username()}",
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["username"]) == 1
    assert (str(response_body["username"][0]) ==
            "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.")


@pytest.mark.django_db
def test_signup_too_short_username(api_client):
    payload = {
        "email": get_random_email(),
        "username": get_too_short_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["username"]) == 1
    assert str(response_body["username"][0]) == "Ensure this field has at least 8 characters."


@pytest.mark.django_db
def test_signup_blank_username(api_client):
    payload = {
        "email": get_random_email(),
        "username": "",
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["username"]) == 1
    assert str(response_body["username"][0]) == "This field may not be blank."


@pytest.mark.django_db
def test_signup_too_long_password(api_client):
    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_too_long_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have a length between 8 and 30."


@pytest.mark.django_db
def test_signup_too_short_password(api_client):
    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_too_short_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have a length between 8 and 30."


@pytest.mark.django_db
def test_signup_password_without_letters(api_client):
    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_password_without_letters(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have at least one letter."


@pytest.mark.django_db
def test_signup_password_without_digits(api_client):
    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_password_without_digits(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have at least one digit."


@pytest.mark.django_db
def test_signup_password_without_space(api_client):
    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_password_without_special_characters(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have at least one special character."


@pytest.mark.django_db
def test_signup(api_client):
    """
    Tests the POST /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    201 Created and the picture, email and username attributes while invalid inputs must return 400 Bad Request.
    """
    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    response = api_client.post(URL, payload)

    assert response.status_code == status.HTTP_201_CREATED
    # Checks that the user was created in the database
    user = User.objects.get(username=payload["username"])
    assert user.email == payload["email"]
    assert user.bio == payload["bio"]
    assert not user.is_active
    assert user.check_password(payload["password"])
    # Checking the response body
    response_body = response.data
    assert response_body.get("username") == payload["username"]
    assert response_body.get("email") == payload["email"]
    assert response_body.get("bio") is not None
    assert response_body.get("picture") == get_profile_picture_base64(user)
    assert len(response_body.get("badges")) == 0
    # Checks that no password is returned
    assert response_body.get("password") is None
    # Check that activation email was sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == SIGN_UP_SUBJECT
    assert SIGN_UP_MESSAGE.split("{}")[1] in mail.outbox[0].body
    assert mail.outbox[0].to == [payload["email"]]
    assert mail.outbox[0].from_email == settings.EMAIL_FROM


@pytest.mark.django_db
def test_signup_repeated_email(api_client, account):
    """
    Tests the POST /user endpoint require unique email and username. In case of repeated email and/or username, 400
    Bad Request must be returned.
    """
    user, _ = account()[0]

    payload = {
        "email": user.email,
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(1, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["email"]) == 1
    assert str(response_body["email"][0]) == "user with this email address already exists."


@pytest.mark.django_db
def test_signup_repeated_username(api_client, account):
    """
    Tests the POST /user endpoint require unique email and username. In case of repeated email and/or username, 400
    Bad Request must be returned.
    """
    user, _ = account()[0]

    payload = {
        "email": get_random_email(),
        "username": user.username,
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(1, 20))
    }

    response = api_client.post(URL, payload)

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["username"]) == 1
    assert str(response_body["username"][0]) == "A user with that username already exists."
