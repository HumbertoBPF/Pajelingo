import base64
import random

import pytest
from django.core import mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import User
from languageschool.tests.utils import get_random_email, get_valid_password, \
    get_too_long_password, get_too_short_password, get_random_username, get_password_without_letters, \
    get_password_without_digits, get_password_without_special_characters, get_too_short_username, get_user_token, \
    assert_badges, attribute_user_badges
from languageschool.utils import SIGN_UP_SUBJECT, SIGN_UP_MESSAGE
from pajelingo import settings

URL = reverse("user-api")
EMAIL = get_random_email()
USERNAME = get_random_username()
PASSWORD = get_valid_password()


def get_profile_picture_base64(user):
    if user.picture:
        img = user.picture.open("rb")
        return base64.b64encode(img.read())


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


@pytest.mark.parametrize(
    "email", [
        EMAIL,
        get_random_string(random.randint(1, 5))+" "+get_random_email(),
        get_random_string(random.randint(0, 16)),
        None
    ]
)
@pytest.mark.parametrize(
    "username", [
        USERNAME,
        get_random_string(random.randint(1, 5))+" "+get_random_username(),
        get_too_short_username(blank=True),
        None
    ]
)
@pytest.mark.parametrize(
    "password", [
        PASSWORD,
        get_too_long_password(),
        get_too_short_password(),
        get_password_without_letters(),
        get_password_without_digits(),
        get_password_without_special_characters(),
        get_random_string(random.randint(0, 2)),
        None
    ]
)
@pytest.mark.parametrize(
    "bio", [
        get_random_string(random.randint(0, 20)),
        None
    ]
)
@pytest.mark.django_db
def test_account_post(api_client, email, username, password, bio):
    """
    Tests the POST /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    201 Created and the picture, email and username attributes while invalid inputs must return 400 Bad Request.
    """
    payload = {}

    if email is not None:
        payload["email"] = email

    if username is not None:
        payload["username"] = username

    if password is not None:
        payload["password"] = password

    if bio is not None:
        payload["bio"] = bio

    response = api_client.post(URL, payload)

    if (email == EMAIL) and (username == USERNAME) and (password == PASSWORD) and (bio is not None):
        assert response.status_code == status.HTTP_201_CREATED
        # Checks that the user was created in the database
        user = User.objects.get(username=username)
        assert user.email == email
        assert user.bio == bio
        assert not user.is_active
        assert user.check_password(password)
        # Checking the response body
        response_body = response.data
        assert response_body.get("username") == username
        assert response_body.get("email") == email
        assert response_body.get("bio") is not None
        assert response_body.get("picture") == get_profile_picture_base64(user)
        assert len(response_body.get("badges")) == 0
        # Checks that no password is returned
        assert response_body.get("password") is None
        # Check that activation email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == SIGN_UP_SUBJECT
        assert SIGN_UP_MESSAGE.split("{}")[1] in mail.outbox[0].body
        assert mail.outbox[0].to == [email]
        assert mail.outbox[0].from_email == settings.EMAIL_FROM
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "repeated_email, repeated_username", [
        (True, True),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.django_db
def test_account_post_requires_unique_email_and_username(api_client, account, repeated_email, repeated_username):
    """
    Tests the POST /user endpoint require unique email and username. In case of repeated email and/or username, 400
    Bad Request must be returned.
    """
    user, _ = account()[0]

    payload = {
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(1, 20))
    }

    if repeated_email:
        payload["email"] = user.email
    else:
        payload["email"] = get_random_email()

    if repeated_username:
        payload["username"] = user.username
    else:
        payload["username"] = get_random_username()

    response = api_client.post(URL, payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


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


@pytest.mark.parametrize(
    "email", [
        EMAIL,
        get_random_string(random.randint(1, 5))+" "+get_random_email(),
        get_random_string(random.randint(0, 16)),
        None
    ]
)
@pytest.mark.parametrize(
    "username", [
        USERNAME,
        get_random_string(random.randint(1, 5))+" "+get_random_username(),
        get_too_short_username(blank=True),
        None
    ]
)
@pytest.mark.parametrize(
    "password", [
        PASSWORD,
        get_too_long_password(),
        get_too_short_password(),
        get_password_without_letters(),
        get_password_without_digits(),
        get_password_without_special_characters(),
        get_random_string(random.randint(0, 2)),
        None
    ]
)
@pytest.mark.parametrize(
    "bio", [
        get_random_string(random.randint(0, 20)),
        None
    ]
)
@pytest.mark.django_db
def test_account_put(api_client, account, email, username, password, bio, badges):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    payload = {}

    if email is not None:
        payload["email"] = email

    if username is not None:
        payload["username"] = username

    if password is not None:
        payload["password"] = password

    if bio is not None:
        payload["bio"] = bio

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    if (email == EMAIL) and (username == USERNAME) and (password == PASSWORD) and (bio is not None):
        assert response.status_code == status.HTTP_200_OK
        # Checking the response body
        response_body = response.data
        assert response_body.get("username") == username
        assert response_body.get("email") == email
        assert response_body.get("bio") is not None
        assert response_body.get("picture") == get_profile_picture_base64(user)
        assert len(response_body.get("badges")) == 2
        assert_badges(response_body.get("badges"), user)
        # Checking that no password is returned
        assert response_body.get("password") is None
        user = User.objects.get(id=user.id)
        assert user.email == email
        assert user.username == username
        assert user.bio == bio
        assert user.check_password(password)
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "repeated_email, repeated_username", [
        (True, True),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.django_db
def test_account_put_requires_unique_email_and_username(api_client, account, repeated_email, repeated_username):
    """
    Tests that the PUT /user endpoint does not accept other users' email and username, returning 400 Bad Request
    for such cases.
    """
    users = account(n=2)
    user, _ = users[0]
    user_to_update, password_user_to_update = users[1]

    payload = {
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(1, 20))
    }

    if repeated_email:
        payload["email"] = user.email
    else:
        payload["email"] = get_random_email()

    if repeated_username:
        payload["username"] = user.username
    else:
        payload["username"] = get_random_username()

    token = get_user_token(api_client, user_to_update, password_user_to_update)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "same_email, same_username", [
        (True, True),
        (True, False),
        (False, True),
        (False, False)
    ]
)
@pytest.mark.django_db
def test_account_put_same_email_and_username(api_client, account, same_email, same_username, badges):
    """
    Tests that the PUT /user endpoint accepts the same email and username.
    """
    user_to_update, password_user_to_update = account()[0]
    attribute_user_badges()

    payload = {
        "password": get_valid_password(),
        "bio": get_random_string(random.randint(1, 20))
    }

    if same_email:
        payload["email"] = user_to_update.email
    else:
        payload["email"] = get_random_email()

    if same_username:
        payload["username"] = user_to_update.username
    else:
        payload["username"] = get_random_username()

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
