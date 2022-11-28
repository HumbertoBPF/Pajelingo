import random

import pytest
from django.utils.crypto import get_random_string

from languageschool.tests.utils import get_valid_password, get_random_email, get_random_username, \
    get_too_short_password, get_too_long_password
from languageschool.validation import is_valid_user_data, ERROR_NOT_CONFIRMED_PASSWORD, ERROR_EMPTY_EMAIL, \
    ERROR_EMPTY_USERNAME, ERROR_EMPTY_PASSWORD, ERROR_LENGTH_PASSWORD, ERROR_SPACE_IN_EMAIL, ERROR_SPACE_IN_USERNAME, \
    ERROR_NOT_AVAILABLE_EMAIL, ERROR_NOT_AVAILABLE_USERNAME

TEST_EMAIL = "test_user@test.com"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "strong-password"


@pytest.mark.parametrize(
    "email", [
        TEST_EMAIL,
        get_random_string(random.randint(1, 10))+" "+get_random_email(),
        ""
    ]
)
@pytest.mark.parametrize(
    "username", [
        TEST_USERNAME,
        get_random_string(random.randint(1, 10))+" "+get_random_username(),
        ""
    ]
)
@pytest.mark.parametrize(
    "password", [
        TEST_PASSWORD,
        get_too_short_password(),
        get_too_long_password()
    ]
)
@pytest.mark.parametrize(
    "is_password_confirmed", [
        True,
        False
    ]
)
@pytest.mark.django_db
def test_validation_function(email, username, password, is_password_confirmed):
    password_confirmation = password if is_password_confirmed else get_valid_password()
    are_valid_inputs = (email == TEST_EMAIL and username == TEST_USERNAME and password == TEST_PASSWORD and is_password_confirmed)
    error_field, error_message = is_valid_user_data(email, username, password, password_confirmation)
    assert (error_field is None) == are_valid_inputs
    assert (error_message is None) == are_valid_inputs


@pytest.mark.parametrize(
    "email, username, password, is_password_confirmed, expected_message", [
        ("", TEST_USERNAME, TEST_PASSWORD, True, ERROR_EMPTY_EMAIL),
        (TEST_EMAIL, "", TEST_PASSWORD, True, ERROR_EMPTY_USERNAME),
        (TEST_EMAIL, TEST_USERNAME, "", True, ERROR_EMPTY_PASSWORD),
        (TEST_EMAIL, TEST_USERNAME, get_too_short_password(), True, ERROR_LENGTH_PASSWORD),
        (TEST_EMAIL, TEST_USERNAME, get_too_long_password(), True, ERROR_LENGTH_PASSWORD),
        (get_random_string(random.randint(1, 10))+" "+get_random_email(), TEST_USERNAME, TEST_PASSWORD, True, ERROR_SPACE_IN_EMAIL),
        (TEST_EMAIL, get_random_string(random.randint(1, 10))+" "+get_random_username(), TEST_PASSWORD, True, ERROR_SPACE_IN_USERNAME),
        (TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, False, ERROR_NOT_CONFIRMED_PASSWORD)
    ]
)
@pytest.mark.django_db
def test_validation_function_error_message(email, username, password, is_password_confirmed, expected_message):
    password_confirmation = password if is_password_confirmed else get_valid_password()
    error_field, error_message = is_valid_user_data(email, username, password, password_confirmation)
    assert error_field is not None
    assert error_message == expected_message


@pytest.mark.parametrize(
    "is_repeated_username, is_repeated_email", [
        (True, True),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.django_db
def test_validation_function_error_message_repeated_credentials_on_signup(account, is_repeated_email, is_repeated_username):
    user, password = account()[0]
    email = user.email if is_repeated_email else get_random_email()
    username = user.username if is_repeated_username else get_random_username()
    new_user_password = get_valid_password()
    error_field, error_message = is_valid_user_data(email, username, new_user_password, new_user_password)

    expected_message = ERROR_NOT_AVAILABLE_EMAIL if is_repeated_email else ERROR_NOT_AVAILABLE_USERNAME
    assert error_field is not None
    assert error_message == expected_message


@pytest.mark.parametrize(
    "is_repeated_username, is_repeated_email", [
        (True, True),
        (True, False),
        (False, True)
    ]
)
@pytest.mark.django_db
def test_validation_function_error_message_repeated_credentials_on_update(account, is_repeated_email, is_repeated_username):
    accounts = account(n=2)
    user, password = accounts[0]
    existing_user, password2 = accounts[1]
    email = user.email if is_repeated_email else get_random_email()
    username = user.username if is_repeated_username else get_random_username()
    new_user_password = get_valid_password()
    error_field, error_message = is_valid_user_data(email, username, new_user_password, new_user_password, existing_user=existing_user)

    expected_message = ERROR_NOT_AVAILABLE_EMAIL if is_repeated_email else ERROR_NOT_AVAILABLE_USERNAME
    assert error_field is not None
    assert error_message == expected_message


@pytest.mark.parametrize(
    "is_same_email", [True, False]
)
@pytest.mark.parametrize(
    "is_same_username", [True, False]
)
@pytest.mark.django_db
def test_validation_function_same_credentials_on_update(account, is_same_email, is_same_username):
    accounts = account(n=2)
    user, password = accounts[0]
    email = user.email if is_same_email else get_random_email()
    username = user.username if is_same_username else get_random_username()
    new_user_password = get_valid_password()
    error_field, error_message = is_valid_user_data(email, username, new_user_password, new_user_password, existing_user=user)

    assert error_field is None
    assert error_message is None
