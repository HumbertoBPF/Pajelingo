import random

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status

from languageschool.forms import FormPicture
from languageschool.models import AppUser
from languageschool.tests.utils import get_valid_password, get_random_email, get_random_username, \
    get_too_long_password, get_too_short_password, get_password_without_letters, get_password_without_digits, \
    get_password_without_special_characters
from languageschool.tests.website.account.validation_function_tests import TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD


@pytest.mark.django_db
def test_profile_access_requires_authentication(client):
    url = reverse('account-profile')
    response = client.get(url)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('account-login')


@pytest.mark.django_db
def test_profile_access(client, account, score, games, languages):
    user, password = account()[0]

    scores = score(users=[user], games=games, languages=languages)

    client.login(username=user.username, password=password)

    url = reverse('account-profile')
    response = client.get(url)

    app_user = response.context.get("app_user")

    assertQuerysetEqual(response.context.get("scores"), scores, ordered=False)
    assert app_user.user.id == user.id
    assert isinstance(response.context.get("form_picture"), FormPicture)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_user_requires_authentication(client):
    url = reverse('account-update-user')

    response = client.get(url)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('account-login')


@pytest.mark.django_db
def test_update_user(client, account):
    user, password = account()[0]
    client.login(username=user.username, password=password)

    url = reverse('account-update-user')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.context.get('user_id') == user.id


@pytest.mark.django_db
def test_do_update_user_requires_authentication(client):
    url = reverse('account-do-update-user')

    response = client.post(url)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('account-login')


@pytest.mark.parametrize(
    "email", [
        TEST_EMAIL,
        get_random_string(random.randint(1, 10)) + " " + get_random_email(),
        ""
    ]
)
@pytest.mark.parametrize(
    "username", [
        TEST_USERNAME,
        get_random_string(random.randint(1, 10)) + " " + get_random_username(),
        ""
    ]
)
@pytest.mark.parametrize(
    "password", [
        TEST_PASSWORD,
        get_too_short_password(),
        get_too_long_password(),
        get_password_without_letters(),
        get_password_without_digits(),
        get_password_without_special_characters()
    ]
)
@pytest.mark.parametrize(
    "is_password_confirmed", [
        True,
        False
    ]
)
@pytest.mark.django_db
def test_do_update_user(client, account, email, username, password, is_password_confirmed):
    user, user_password = account()[0]
    client.login(username=user.username, password=user_password)

    url = reverse('account-do-update-user')
    data = {
        "email": email,
        "username": username,
        "password": password,
        "password_confirmation": password if is_password_confirmed else get_valid_password()
    }

    response = client.post(url, data=data)

    is_user_updated = (email == TEST_EMAIL) and (username == TEST_USERNAME) and (
            password == TEST_PASSWORD) and is_password_confirmed
    assert response.status_code == status.HTTP_302_FOUND if is_user_updated else status.HTTP_200_OK
    assert User.objects.filter(id=user.id,
                               email=email if is_user_updated else user.email,
                               username=username if is_user_updated else user.username).exists()
    assert AppUser.objects.filter(user__id=user.id,
                                  user__email=email if is_user_updated else user.email,
                                  user__username=username if is_user_updated else user.username).exists()


@pytest.mark.parametrize(
    "is_repeated_email, is_repeated_username", [
        (True, True),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.django_db
def test_do_update_user_repeated_credentials(client, account, is_repeated_email, is_repeated_username):
    accounts = account(n=2)
    user, password = accounts[0]
    user2, password2 = accounts[1]
    client.login(username=user.username, password=password)

    url = reverse('account-do-update-user')
    new_password = get_valid_password()
    data = {
        "email": user2.email if is_repeated_email else get_random_email(),
        "username": user2.username if is_repeated_username else get_random_username(),
        "password": new_password,
        "password_confirmation": new_password
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_302_FOUND
    assert User.objects.filter(id=user.id, email=user.email, username=user.username).exists()
    assert AppUser.objects.filter(user__id=user.id, user__email=user.email, user__username=user.username).exists()


@pytest.mark.parametrize(
    "is_same_email, is_same_username", [
        (True, True),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.django_db
def test_do_update_user_same_credentials(client, account, is_same_email, is_same_username):
    user, password = account()[0]
    client.login(username=user.username, password=password)

    url = reverse('account-do-update-user')
    new_password = get_valid_password()
    data = {
        "email": user.email if is_same_email else get_random_email(),
        "username": user.username if is_same_username else get_random_username(),
        "password": new_password,
        "password_confirmation": new_password
    }

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_302_FOUND
    assert User.objects.filter(id=user.id, email=data["email"], username=data["username"]).exists()
    assert AppUser.objects.filter(user__id=user.id, user__email=data["email"], user__username=data["username"]).exists()


@pytest.mark.django_db
def test_delete_user_requires_authentication(client, account):
    user, password = account()[0]
    url = reverse('account-delete-user')
    response = client.post(url)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('account-login')
    assert User.objects.filter(id=user.id, email=user.email, username=user.username).exists()
    assert AppUser.objects.filter(user__id=user.id, user__email=user.email, user__username=user.username).exists()


@pytest.mark.django_db
def test_delete_user(client, account):
    user, password = account()[0]
    client.login(username=user.username, password=password)

    url = reverse('account-delete-user')

    response = client.post(url)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('index')
    assert not User.objects.filter(id=user.id, email=user.email, username=user.username).exists()
    assert not AppUser.objects.filter(user__id=user.id, user__email=user.email, user__username=user.username).exists()


@pytest.mark.django_db
def test_change_profile_picture_requires_authentication(client, account):
    user, password = account()[0]
    url = reverse('account-change-picture')

    response = client.post(url)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == reverse('account-login')
    assert AppUser.objects.filter(user__id=user.id, user__email=user.email, user__username=user.username) \
               .first().picture == ""


@pytest.mark.parametrize(
    "filename, is_successful", [
        ('C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/pajelingo/static/pajelingo.jpg', True),
        ('C:/Users/Humberto/Downloads/PokemonApp.pdf', False),
        ('C:/Users/Humberto/Downloads/test.txt', False)
    ]
)
@pytest.mark.django_db
def test_change_profile_picture(client, account, filename, is_successful):
    user, password = account()[0]
    client.login(username=user.username, password=password)

    url = reverse('account-change-picture')

    with open(filename, 'rb') as fp:
        response = client.post(url, data={'picture': fp})
        assert response.status_code == status.HTTP_302_FOUND
        assert response.url == reverse('account-profile')
        assert (AppUser.objects.filter(user__id=user.id, user__email=user.email, user__username=user.username)
                .first().picture != "") == is_successful
