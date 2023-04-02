import time

import pytest
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import assert_is_login_page, authenticate_user, \
    wait_number_of_elements_to_be, find_element, assert_is_profile_page
from languageschool.tests.utils import get_random_username, get_valid_password, get_random_email, \
    get_too_short_username, get_too_short_password, get_too_long_password, get_password_without_letters, \
    get_password_without_digits, get_password_without_special_characters
from pajelingo.settings import FRONT_END_URL

UPDATE_ACCOUNT_URL = FRONT_END_URL + "/update-account"
CSS_SELECTOR_FORM_INPUTS = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-info")
CSS_SELECTOR_VALIDATION_WARNING = (By.CSS_SELECTOR, "main form .invalid-feedback ul li")
CSS_SELECTOR_ALERT_TOAST = (By.CSS_SELECTOR, "main .toast-container .toast")


@pytest.mark.django_db
def test_update_account_requires_authentication(live_server, selenium_driver):
    selenium_driver.get(UPDATE_ACCOUNT_URL)
    assert_is_login_page(selenium_driver)


@pytest.mark.django_db
def test_update_account_form_rendering(live_server, selenium_driver, account):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(UPDATE_ACCOUNT_URL)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUTS, 4)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUTS[0], CSS_SELECTOR_FORM_INPUTS[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    assert len(form_inputs) == 4
    assert form_inputs[0].get_attribute("value") == user.email
    assert form_inputs[1].get_attribute("value") == user.username
    assert submit_button.text == "Update"


@pytest.mark.parametrize(
    "email, username, password, confirm_password, feedback", [
        (None, get_random_username(), get_valid_password(), True, "This field is required."),
        (get_random_string(8), get_random_username(), get_valid_password(), True, "Enter a valid email address."),
        (get_random_email(), None, get_valid_password(), True, "This field is required."),
        (get_random_email(), get_random_username() + " " + get_random_string(1), get_valid_password(), True,
         "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."),
        (get_random_email(), get_too_short_username(), get_valid_password(), True,
         "The username must be at least 8 characters-long."),
        (get_random_email(), get_random_username(), None, True,
         "This field is required."),
        (get_random_email(), get_random_username(), get_too_short_password(), True,
         "The password must have a length between 8 and 30."),
        (get_random_email(), get_random_username(), get_too_long_password(), True,
         "The password must have a length between 8 and 30."),
        (get_random_email(), get_random_username(), get_password_without_letters(), True,
         "The password must have at least one letter."),
        (get_random_email(), get_random_username(), get_password_without_digits(), True,
         "The password must have at least one digit."),
        (get_random_email(), get_random_username(), get_password_without_special_characters(), True,
         "The password must have at least one special character."),
        (get_random_email(), get_random_username(), get_valid_password(), None, "This field is required."),
        (get_random_email(), get_random_username(), get_valid_password(), False, "The passwords do not match.")
    ]
)
def test_update_account_form_validation(live_server, selenium_driver, account, email, username, password,
                                        confirm_password, feedback):
    user, user_password = account()[0]

    authenticate_user(selenium_driver, user.username, user_password)

    selenium_driver.get(UPDATE_ACCOUNT_URL)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUTS, 4)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUTS[0], CSS_SELECTOR_FORM_INPUTS[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    email = "" if (email is None) else email
    username = "" if (username is None) else username
    password = "" if (password is None) else password

    form_inputs[0].clear()
    form_inputs[0].send_keys(email)

    form_inputs[1].clear()
    form_inputs[1].send_keys(username)

    form_inputs[2].send_keys(password)

    if confirm_password is None:
        form_inputs[3].send_keys("")
    else:
        form_inputs[3].send_keys(password if confirm_password else get_random_string(5) + password)

    submit_button.click()

    form_validation_warnings = find_element(selenium_driver, CSS_SELECTOR_VALIDATION_WARNING)

    assert form_validation_warnings.text == feedback


@pytest.mark.parametrize(
    "is_repeated_email, is_repeated_username", [
        (True, False),
        (False, True),
        (True, True)
    ]
)
@pytest.mark.django_db
def test_update_account_repeated_credentials(live_server, selenium_driver, account, is_repeated_email, is_repeated_username):
    accounts = account(n=2)

    user, user_password = accounts[0]
    another_user, _ = accounts[1]

    authenticate_user(selenium_driver, user.username, user_password)

    selenium_driver.get(UPDATE_ACCOUNT_URL)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUTS, 4)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUTS[0], CSS_SELECTOR_FORM_INPUTS[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    email = another_user.email if is_repeated_email else get_random_email()
    username = another_user.username if is_repeated_username else get_random_username()
    password = get_valid_password()

    form_inputs[0].send_keys(email)
    form_inputs[1].send_keys(username)
    form_inputs[2].send_keys(password)
    form_inputs[3].send_keys(password)

    submit_button.click()

    alert_toast = find_element(selenium_driver, CSS_SELECTOR_ALERT_TOAST)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to update account. Please check the information provided."


@pytest.mark.parametrize("is_same_username", [True, False])
@pytest.mark.parametrize("is_same_email", [True, False])
@pytest.mark.django_db
def test_update_account_same_credentials(live_server, selenium_driver, account, is_same_username, is_same_email):
    user, user_password = account()[0]

    authenticate_user(selenium_driver, user.username, user_password)

    selenium_driver.get(UPDATE_ACCOUNT_URL)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUTS, 4)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUTS[0], CSS_SELECTOR_FORM_INPUTS[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    email = user.email if is_same_email else get_random_email()
    username = user.username if is_same_username else get_random_username()
    password = get_valid_password()

    form_inputs[0].clear()
    form_inputs[0].send_keys(email)
    form_inputs[1].clear()
    form_inputs[1].send_keys(username)
    form_inputs[2].send_keys(password)
    form_inputs[3].send_keys(password)

    submit_button.click()

    assert_is_profile_page(selenium_driver, username, email)
    assert User.objects.filter(
        id=user.id,
        email=email,
        username=username
    ).exists()
