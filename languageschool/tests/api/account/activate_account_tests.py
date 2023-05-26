import uuid

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.authtoken.admin import User

from pajelingo.tokens import account_activation_token


@pytest.mark.parametrize(
    "has_uuid, has_token",[
        (True, False),
        (False, True),
        (False, False)
    ]
)
@pytest.mark.django_db
def test_activate_account_not_found_url(api_client, has_uuid, has_token):
    """
    Tests that /api/activate/<uidb64>/<token> raises a 404 Not Found if the URL is not built properly.
    """
    url = "api/activate"

    if has_uuid:
        uid = uuid.uuid4()
        url += "/{}".format(uid)

    if has_token:
        token = get_random_string(8)
        url += "/{}".format(token)

    response = api_client.put(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_activate_account_uuid_does_not_have_correct_format(api_client, account):
    """
    Tests that /api/activate/<uidb64>/<token> raises a 403 Forbidden if the uuid specified as path parameter does not
    have the required format (base 64 encoded UUID).
    """
    user, password = account()[0]

    url = reverse("activate-account-api", kwargs={
        "uidb64": uuid.uuid4(),
        "token": account_activation_token.make_token(user)
    })

    response = api_client.put(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_activate_account_uuid_does_not_match_any_user(api_client, account):
    """
    Tests that /api/activate/<uidb64>/<token> raises a 403 Forbidden if the uuid specified as path parameter does not
    match any user.
    """
    user, password = account()[0]

    uid = urlsafe_base64_encode(force_bytes(user.pk + 100))

    url = reverse("activate-account-api", kwargs={
        "uidb64": uid,
        "token": account_activation_token.make_token(user)
    })

    response = api_client.put(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_activate_account_uuid_does_not_match_active_user(api_client, account):
    """
    Tests that /api/activate/<uidb64>/<token> raises a 403 Forbidden if the uuid specified as path parameter does not
    match any inactive user.
    """
    user, password = account()[0]

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    url = reverse("activate-account-api", kwargs={
        "uidb64": uid,
        "token": account_activation_token.make_token(user)
    })

    response = api_client.put(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_activate_account_uuid_invalid_token(api_client, account):
    """
    Tests that /api/activate/<uidb64>/<token> raises a 403 Forbidden if the token specified as path parameter is not
    valid.
    """
    user, password = account(is_active=False)[0]

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    url = reverse("activate-account-api", kwargs={
        "uidb64": uid,
        "token": get_random_string(8)
    })

    response = api_client.put(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_activate_account(api_client, account):
    """
    Tests that /api/activate/<uidb64>/<token> with valid path parameters activates the concerned user.
    """
    user, password = account(is_active=False)[0]

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    url = reverse("activate-account-api", kwargs={
        "uidb64": uid,
        "token": token
    })

    response = api_client.put(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    user = User.objects.get(id=user.id)
    assert user.is_active
