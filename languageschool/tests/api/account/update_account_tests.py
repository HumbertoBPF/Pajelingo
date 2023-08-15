import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import User
from languageschool.tests.utils import get_random_username, get_user_token, attribute_user_badges, get_valid_password, \
    get_random_email, get_profile_picture_base64, assert_badges, get_too_long_password, get_too_short_password, \
    get_password_without_letters, get_password_without_digits, get_password_without_special_characters, \
    get_too_short_username

URL = reverse("user-api")


@pytest.mark.django_db
def test_account_put_requires_authentication(api_client):
    """
    Tests that the PUT /user endpoint requires token authentication.
    """
    response = api_client.put(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_put_wrong_credentials(api_client):
    """
    Tests that the PUT /user endpoint returns 401 Unauthorized when an invalid token is used.
    """
    response = api_client.put(URL, HTTP_AUTHORIZATION="Token {}".format(get_random_string(16)))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("field", ["email", "username", "password", "bio"])
@pytest.mark.django_db
def test_account_put_required_params(api_client, account, badges, field):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    del payload[field]

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body[field]) == 1
    assert str(response_body[field][0]) == "This field is required."


@pytest.mark.django_db
def test_account_put_email_with_space(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": f"{get_random_string(random.randint(1, 5))} {get_random_email()}",
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["email"]) == 1
    assert str(response_body["email"][0]) == "Enter a valid email address."


@pytest.mark.django_db
def test_account_put_blank_email(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": "",
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["email"]) == 1
    assert str(response_body["email"][0]) == "This field may not be blank."


@pytest.mark.django_db
def test_account_put_email_wrong_format(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_string(random.randint(1, 16)),
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["email"]) == 1
    assert str(response_body["email"][0]) == "Enter a valid email address."


@pytest.mark.django_db
def test_account_put_username_with_space(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": f"{get_random_string(random.randint(1, 5))} {get_random_username()}",
        "password": get_valid_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["username"]) == 1
    assert (str(response_body["username"][0]) ==
            "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.")


@pytest.mark.django_db
def test_account_put_too_short_username(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": get_too_short_username(),
        "password": get_valid_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["username"]) == 1
    assert str(response_body["username"][0]) == "Ensure this field has at least 8 characters."


@pytest.mark.django_db
def test_account_put_blank_username(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": "",
        "password": get_valid_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["username"]) == 1
    assert str(response_body["username"][0]) == "This field may not be blank."


@pytest.mark.django_db
def test_account_put_too_short_password(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_too_short_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have a length between 8 and 30."


@pytest.mark.django_db
def test_account_put_too_long_password(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_too_long_password(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have a length between 8 and 30."


@pytest.mark.django_db
def test_account_put_password_with_no_letters(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_password_without_letters(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have at least one letter."


@pytest.mark.django_db
def test_account_put_password_with_no_digits(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_password_without_digits(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have at least one digit."


@pytest.mark.django_db
def test_account_put_password_with_no_special_characters(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_password_without_special_characters(),
        "bio":get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["password"]) == 1
    assert str(response_body["password"][0]) == "The password must have at least one special character."


@pytest.mark.django_db
def test_account_put(api_client, account, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {
        "email": get_random_email(),
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(0, 20))
    }

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_200_OK
    # Checking the response body
    response_body = response.data
    assert response_body.get("username") == payload["username"]
    assert response_body.get("email") == payload["email"]
    assert response_body.get("bio") is not None
    assert response_body.get("picture") == get_profile_picture_base64(user)
    assert len(response_body.get("badges")) == 2
    assert_badges(response_body.get("badges"), user)
    # Checking that no password is returned
    assert response_body.get("password") is None
    user = User.objects.get(id=user.id)
    assert user.email == payload["email"]
    assert user.username == payload["username"]
    assert user.bio == payload["bio"]
    assert user.check_password(payload["password"])


@pytest.mark.django_db
def test_account_put_repeated_email(api_client, account):
    """
    Tests that the PUT /user endpoint does not accept other users' email and username, returning 400 Bad Request
    for such cases.
    """
    users = account(n=2)
    user, _ = users[0]
    user_to_update, password_user_to_update = users[1]

    payload = {
        "email": user.email,
        "username": get_random_username(),
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(1, 20))
    }

    token = get_user_token(api_client, user_to_update, password_user_to_update)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["email"]) == 1
    assert str(response_body["email"][0]) == "user with this email address already exists."


@pytest.mark.django_db
def test_account_put_repeated_username(api_client, account):
    """
    Tests that the PUT /user endpoint does not accept other users' email and username, returning 400 Bad Request
    for such cases.
    """
    users = account(n=2)
    user, _ = users[0]
    user_to_update, password_user_to_update = users[1]

    payload = {
        "email": get_random_email(),
        "username": user.username,
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(1, 20))
    }

    token = get_user_token(api_client, user_to_update, password_user_to_update)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    response_body = response.data

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(response_body) == 1
    assert len(response_body["username"]) == 1
    assert str(response_body["username"][0]) == "A user with that username already exists."


@pytest.mark.django_db
def test_account_put_same_email_and_username(api_client, account, badges):
    """
    Tests that the PUT /user endpoint accepts the same email and username.
    """
    user_to_update, password_user_to_update = account()[0]
    attribute_user_badges()

    payload = {
        "email": user_to_update.email,
        "username": user_to_update.username,
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(1, 20))
    }

    token = get_user_token(api_client, user_to_update, password_user_to_update)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_200_OK
    # Checking the response body
    response_body = response.data
    assert response_body.get("username") == payload["username"]
    assert response_body.get("email") == payload["email"]
    assert response_body.get("bio") == payload["bio"]
    assert response_body.get("picture") == get_profile_picture_base64(user_to_update)
    assert len(response_body.get("badges")) == 2
    assert_badges(response_body.get("badges"), user_to_update)
    # Checking that no password is returned
    assert response_body.get("password") is None
    # Checking that the concerned user was updated
    user = User.objects.get(id=user_to_update.id)
    assert user.username == payload["username"]
    assert user.email == payload["email"]
    assert user.bio == payload["bio"]
    assert user.check_password(payload["password"])