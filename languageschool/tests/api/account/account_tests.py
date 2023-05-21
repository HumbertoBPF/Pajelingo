import base64
import random

import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.tests.utils import get_random_email, get_valid_password, \
    get_too_long_password, get_too_short_password, get_random_username, get_password_without_letters, \
    get_password_without_digits, get_password_without_special_characters, get_too_short_username, get_user_token
from languageschool.utils import SIGN_UP_SUBJECT, SIGN_UP_MESSAGE
from pajelingo import settings

URL = reverse("user-api")
EMAIL = get_random_email()
USERNAME = get_random_username()
PASSWORD = get_valid_password()


def get_profile_picture_base64(user):
    # app_user = AppUser.objects.filter(user__id=user.id).first()
    # if app_user.picture:
    #     img = app_user.picture.open("rb")
    #     return base64.b64encode(img.read())
    pass


@pytest.mark.django_db
def test_account_get_requires_authentication(api_client):
    """
    Tests that the GET /user endpoint requires token authentication.
    """
    response = api_client.get(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_get_wrong_token(api_client, account):
    """
    Tests that the GET /user endpoint returns 401 Unauthorized when an invalid token is used.
    """
    _, _ = account()[0]
    response = api_client.get(URL, HTTP_AUTHORIZATION="Token {}".format(get_random_string(16)))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_get(api_client, account):
    """
    Tests that the GET /user endpoint returns 200 when the credentials are correct.
    """
    user, password = account()[0]

    token = get_user_token(api_client, user, password)

    response = api_client.get(URL, HTTP_AUTHORIZATION="Token {}".format(token))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("username") == user.username
    assert response.data.get("email") == user.email
    assert response.data.get("picture") == get_profile_picture_base64(user)


@pytest.mark.parametrize(
    "email", [
        EMAIL,
        get_random_string(random.randint(1, 5))+" "+get_random_email(),
        get_random_string(random.randint(1, 16)),
        "",
        None
    ]
)
@pytest.mark.parametrize(
    "username", [
        USERNAME,
        get_random_string(random.randint(1, 5))+" "+get_random_username(),
        get_too_short_username(),
        "",
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
        "",
        None
    ]
)
@pytest.mark.django_db
def test_account_post(api_client, email, username, password):
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

    response = api_client.post(URL, payload)

    if (email == EMAIL) and (username == USERNAME) and (password == PASSWORD):
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get("username") == username
        assert response.data.get("email") == email
        user = User.objects.filter(email=email, username=username, is_active=False).first()
        assert user is not None
        # assert AppUser.objects.filter(
        #     user__email=email,
        #     user__username=username
        # ).exists()
        assert response.data.get("picture") == get_profile_picture_base64(user)
        # Check that activation email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == SIGN_UP_SUBJECT
        assert SIGN_UP_MESSAGE.split("{}")[1] in mail.outbox[0].body
        assert mail.outbox[0].to == [email]
        assert mail.outbox[0].from_email == settings.EMAIL_FROM
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.count() == 0


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
        "password": get_valid_password()
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
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_account_put_requires_authentication(api_client):
    """
    Tests that the PUT /user endpoint requires token authentication.
    """
    response = api_client.put(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_put_wrong_credentials(api_client, account):
    """
    Tests that the PUT /user endpoint returns 401 Unauthorized when an invalid token is used.
    """
    _, _ = account()[0]
    response = api_client.put(URL, HTTP_AUTHORIZATION="Token {}".format(get_random_string(16)))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "email", [
        EMAIL,
        get_random_string(random.randint(1, 5))+" "+get_random_email(),
        get_random_string(random.randint(1, 16)),
        "",
        None
    ]
)
@pytest.mark.parametrize(
    "username", [
        USERNAME,
        get_random_string(random.randint(1, 5))+" "+get_random_username(),
        get_too_short_username(),
        "",
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
        "",
        None
    ]
)
@pytest.mark.django_db
def test_account_put(api_client, account, email, username, password):
    """
    Tests the PUT /user endpoint with several inputs. One of the combinations (EMAIL, USERNAME, PASSWORD) must return
    200 Ok and the picture, email, and username attributes while invalid inputs must return 400 Bad Request.
    """
    user, user_password = account()[0]

    payload = {}

    if email is not None:
        payload["email"] = email

    if username is not None:
        payload["username"] = username

    if password is not None:
        payload["password"] = password

    token = get_user_token(api_client, user, user_password)

    response = api_client.put(URL, payload, HTTP_AUTHORIZATION="Token {}".format(token))

    if (email == EMAIL) and (username == USERNAME) and (password == PASSWORD):
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("username") == username
        assert response.data.get("email") == email
        assert response.data.get("picture") == get_profile_picture_base64(user)
        assert User.objects.filter(id=user.id, email=email, username=username).exists()
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(id=user.id, email=email, username=username).exists()


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
        "password": get_valid_password()
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
    assert User.objects.count() == 2
    assert User.objects.filter(id=user.id, username=user.username, email=user.email).exists()
    assert User.objects\
        .filter(id=user_to_update.id, username=user_to_update.username, email=user_to_update.email).exists()


@pytest.mark.parametrize(
    "same_email, same_username", [
        (True, True),
        (True, False),
        (False, True),
        (False, False)
    ]
)
@pytest.mark.django_db
def test_account_put_same_email_and_username(api_client, account, same_email, same_username):
    """
    Tests that the PUT /user endpoint accepts the same email and username.
    """
    users = account(n=2)
    user, _ = users[0]
    user_to_update, password_user_to_update = users[1]

    payload = {
        "password": get_valid_password()
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
    assert User.objects.count() == 2
    assert User.objects.filter(id=user.id, username=user.username, email=user.email).exists()
    assert User.objects.filter(id=user_to_update.id, username=payload["username"], email=payload["email"]).exists()


@pytest.mark.django_db
def test_account_delete_requires_authentication(api_client):
    """
    Tests that the DELETE /user endpoint requires token authentication.
    """
    response = api_client.delete(URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_account_delete_wrong_credentials(api_client, account):
    """
    Tests that the DELETE /user endpoint returns 401 Unauthorized when an invalid token is used.
    """
    _, _ = account()[0]
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
