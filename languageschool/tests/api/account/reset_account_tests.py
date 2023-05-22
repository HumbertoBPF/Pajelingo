import string
import uuid

import pytest
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from languageschool.models import User
from languageschool.tests.utils import get_too_long_password, get_too_short_password, get_password_without_letters, \
    get_password_without_digits, get_password_without_special_characters, get_valid_password

REQUEST_RESET_ACCOUNT_URL = reverse("request-reset-account-api")


@pytest.mark.django_db
def test_reset_account_requires_email_parameter(api_client):
    """
    Tests that /api/request-reset-account raises a 400 Bad Request when no email parameter is sent.
    """
    response = api_client.post(REQUEST_RESET_ACCOUNT_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_request_reset_account_validates_email_parameter_format(api_client):
    """
    Tests that /api/request-reset-account raises a 400 Bad Request if the email parameter does not have an email format.
    """
    response = api_client.post(REQUEST_RESET_ACCOUNT_URL, data={
        "email": get_random_string(8, string.ascii_letters)
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_request_reset_account_email_does_not_match_account(api_client):
    """
    Tests that /api/request-reset-account returns a 200 Ok if the email parameter does not match an existing account,
    but no email is sent.
    """
    response = api_client.post(REQUEST_RESET_ACCOUNT_URL, data={
        "email": get_random_string(8, string.ascii_letters) + "@test.com"
    })

    assert response.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_request_reset_account_email_does_not_match_active_account(api_client, account):
    """
    Tests that /api/request-reset-account returns a 200 Ok if the email parameters does not match an active account,
    but no email is sent.
    """
    user, password = account()[0]
    user.is_active = False
    user.save()

    response = api_client.post(REQUEST_RESET_ACCOUNT_URL, data={
        "email": user.email
    })

    assert response.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_request_reset_account(api_client, account):
    """
    Tests that /api/request-reset-account returns 200 Ok when an active user email is specified and a reset account
    email is sent for this email.
    """
    user, password = account()[0]

    response = api_client.post(REQUEST_RESET_ACCOUNT_URL, data={
        "email": user.email
    })

    assert response.status_code == status.HTTP_200_OK
    assert len(mail.outbox) == 1
    assert len(mail.outbox[0].to) == 1
    assert mail.outbox[0].to[0] == user.email
    assert mail.outbox[0].subject == "Pajelingo account reset"


@pytest.mark.parametrize(
    "has_uuid, has_token",[
        (True, False),
        (False, True),
        (False, False)
    ]
)
@pytest.mark.django_db
def test_reset_account_not_found_url(api_client, has_uuid, has_token):
    """
    Tests that /api/reset-account returns 404 Not Found when some path parameter is missing.
    """
    url = "api/reset-account"

    if has_uuid:
        uid = uuid.uuid4()
        url += "/{}".format(uid)

    if has_token:
        token = get_random_string(8)
        url += "/{}".format(token)

    response = api_client.put(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_reset_account_requires_password(api_client, account):
    """
    Tests that /api/reset-password raises 400 Bad Request if no password parameter is sent.
    """
    user, _ = account()[0]

    url = reverse("reset-account-api", kwargs={
        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user)
    })

    response = api_client.put(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "password", [
        get_too_long_password(),
        get_too_short_password(),
        get_password_without_letters(),
        get_password_without_digits(),
        get_password_without_special_characters(),
        ""
    ]
)
@pytest.mark.django_db
def test_reset_account_validates_password(api_client, account, password):
    """
    Tests that /api/reset-account raises a 400 Bad Request if the specified password does not fulfill all validation
    rules.
    """
    user, _ = account()[0]

    url = reverse("reset-account-api", kwargs={
        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user)
    })

    response = api_client.put(url, data={
        "password": password
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_reset_account_uuid_does_not_have_required_format(api_client, account):
    """
    Test that /api/reset-account raises a 403 Forbidden when the uuid parameter is not in the right format (base 64
    encoded UUID).
    """
    user, _ = account()[0]

    url = reverse("reset-account-api", kwargs={
        "uidb64": uuid.uuid4(),
        "token": default_token_generator.make_token(user)
    })

    response = api_client.put(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_reset_account_uuid_does_not_match_any_user(api_client, account):
    """
    Test that /api/reset-account raises a 403 Forbidden when the user encoded in the uuid parameter does not exist.
    """
    user, _ = account()[0]

    url = reverse("reset-account-api", kwargs={
        "uidb64": urlsafe_base64_encode(force_bytes(user.id + 100)),
        "token": default_token_generator.make_token(user)
    })

    response = api_client.put(url, data={
        "password": get_valid_password()
    })

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_reset_account_uuid_does_not_match_active_user(api_client, account):
    """
    Test that /api/reset-account raises a 403 Forbidden when the user encoded in the uuid parameter is not active.
    """
    user, _ = account()[0]
    user.is_active = False
    user.save()

    url = reverse("reset-account-api", kwargs={
        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user)
    })

    response = api_client.put(url, data={
        "password": get_valid_password()
    })

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_reset_account_invalid_token(api_client, account):
    """
    Tests that /api/reset-account raises a 403 Forbidden when an invalid token is sent.
    """
    user, _ = account()[0]

    url = reverse("reset-account-api", kwargs={
        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": get_random_string(8)
    })

    response = api_client.put(url, data={
        "password": get_valid_password()
    })

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_reset_account(api_client, account):
    """
    Tests that /api/reset-account redefines the user's password when all the required parameters are valid.
    """
    user, _ = account()[0]
    password = get_valid_password()

    url = reverse("reset-account-api", kwargs={
        "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user)
    })

    response = api_client.put(url, data={
        "password": password
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT
    updated_user = User.objects.filter(id=user.id).first()
    assert check_password(password, updated_user.password)
