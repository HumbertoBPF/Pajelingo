import random

import pytest
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status

from languageschool.models import AppUser
from languageschool.tests.website.account.validation_function_tests import TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD


@pytest.mark.parametrize(
    "email", [
        TEST_EMAIL,
        get_random_string(random.randint(1, 15))+" "+get_random_string(random.randint(1, 15))+"@test.com",
        ""
    ]
)
@pytest.mark.parametrize(
    "username", [
        TEST_USERNAME,
        get_random_string(random.randint(1, 15))+" "+get_random_string(random.randint(1, 15)),
        ""
    ]
)
@pytest.mark.parametrize(
    "password", [
        TEST_PASSWORD,
        get_random_string(random.randint(1, 5)),
        get_random_string(random.randint(31, 50))
    ]
)
@pytest.mark.parametrize(
    "is_password_confirmed", [
        True,
        False
    ]
)
@pytest.mark.django_db
def test_signup_validation(client, email, username, password, is_password_confirmed):
    url = reverse('account-create-user')
    data = {
        "email": email,
        "username": username,
        "password": password,
        "password_confirmation": password if is_password_confirmed else get_random_string(random.randint(1, 50))
    }

    response = client.post(url, data=data)
    is_user_created = (email == TEST_EMAIL) and (username == TEST_USERNAME) and (password == TEST_PASSWORD) and is_password_confirmed
    assert response.status_code == status.HTTP_302_FOUND if is_user_created else status.HTTP_200_OK
    assert User.objects.filter(email=email, username=username).exists() == is_user_created
    assert AppUser.objects.filter(user__email=email, user__username=username).exists() == is_user_created


@pytest.mark.parametrize(
    "is_repeated_email, is_repeated_username", [
        (True, True),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.django_db
def test_signup_error_repeated_credentials(client, account, is_repeated_email, is_repeated_username):
    user, password = account()[0]
    password_signup = get_random_string(random.randint(6, 30))

    url = reverse('account-create-user')
    data = {
        "email": user.email if is_repeated_email else get_random_string(random.randint(10, 30))+"@test.com",
        "username": user.username if is_repeated_username else get_random_string(random.randint(10, 30)),
        "password": password_signup,
        "password_confirmation": password_signup
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert not User.objects.filter(~Q(id=user.id), email=data["email"], username=data["username"]).exists()
    assert not AppUser.objects.filter(~Q(id=user.id), user__email=data["email"], user__username=data["username"])\
        .exists()
