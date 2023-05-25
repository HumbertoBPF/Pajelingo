import pytest
from django.contrib.auth.hashers import check_password
from django.core import mail
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import User
from languageschool.tests.selenium.utils import find_element, CSS_SELECTOR_USER_FORM_INPUTS, \
    CSS_SELECTOR_USER_FORM_SUBMIT_BUTTON, submit_user_form
from languageschool.tests.utils import get_random_username, get_valid_password, get_random_email, \
    get_too_short_username, get_too_short_password, get_too_long_password, get_password_without_letters, \
    get_password_without_digits, get_password_without_special_characters, get_random_bio
from pajelingo.settings import FRONT_END_URL

SIGNUP_URL = FRONT_END_URL + "/signup"
CSS_SELECTOR_VALIDATION_WARNING = (By.CSS_SELECTOR, "main form .invalid-feedback ul li")
CSS_SELECTOR_ALERT_TOAST = (By.CSS_SELECTOR, "main .toast-container .toast")
CSS_SELECTOR_ALERT_SUCCESS = (By.CSS_SELECTOR, "main .alert-success")


def test_signup_form_rendering(live_server, selenium_driver):
    selenium_driver.get(SIGNUP_URL)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_USER_FORM_INPUTS[0], CSS_SELECTOR_USER_FORM_INPUTS[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_USER_FORM_SUBMIT_BUTTON)

    assert len(form_inputs) == 5
    assert submit_button.text == "Sign up"


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
def test_signup_form_validation(live_server, selenium_driver, email, username, password, confirm_password, feedback):
    selenium_driver.get(SIGNUP_URL)

    email = "" if (email is None) else email
    username = "" if (username is None) else username
    bio = get_random_bio()
    password = "" if (password is None) else password

    submit_user_form(selenium_driver, email, username, bio, password, confirm_password)

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
def test_signup_repeated_credentials(live_server, selenium_driver, account, is_repeated_email, is_repeated_username):
    user, password = account()[0]

    selenium_driver.get(SIGNUP_URL)

    email = user.email if is_repeated_email else get_random_email()
    username = user.username if is_repeated_username else get_random_username()
    bio = get_random_bio()
    password = get_valid_password()

    submit_user_form(selenium_driver, email, username, bio, password, True)

    alert_toast = find_element(selenium_driver, CSS_SELECTOR_ALERT_TOAST)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to create account. Please check the information provided."


def test_signup(live_server, selenium_driver):
    selenium_driver.get(SIGNUP_URL)

    email = get_random_email()
    username = get_random_username()
    bio = get_random_bio()
    password = get_valid_password()

    submit_user_form(selenium_driver, email, username, bio, password, True)

    alert_success = find_element(selenium_driver, CSS_SELECTOR_ALERT_SUCCESS)
    alert_success_text = alert_success.find_element(By.CSS_SELECTOR, "p")

    assert alert_success_text.text == "Account successfully created. Please check your email to activate it."

    user = User.objects.filter(
        email=email,
        username=username,
        bio=bio
    ).first()
    assert user is not None
    check_password(password, user.password)

    assert len(mail.outbox) == 1
    signup_email = mail.outbox[0]
    assert signup_email.subject == "Pajelingo account activation"
    assert "Hi {},\n\nPlease click on the link below to activate your Pajelingo account:\n\n{}"\
        .format(username, FRONT_END_URL) in signup_email.body
    assert len(signup_email.to) == 1
    assert signup_email.to[0] == email
