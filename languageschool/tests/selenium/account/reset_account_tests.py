import pytest
from django.contrib.auth.hashers import check_password
from django.core import mail
from django.utils.crypto import get_random_string
from rest_framework.authtoken.admin import User
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_element, wait_number_of_elements_to_be
from languageschool.tests.utils import get_valid_password, get_password_without_special_characters, \
    get_password_without_digits, get_password_without_letters, get_too_long_password, get_too_short_password
from pajelingo.settings import FRONT_END_URL

REQUEST_RESET_ACCOUNT_URL = FRONT_END_URL + "/request-reset-account"
CSS_SELECTOR_FORM_INPUT = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")
CSS_SELECTOR_VALIDATION_WARNING = (By.CSS_SELECTOR, "main form .invalid-feedback ul li")
CSS_SELECTOR_ALERT_TOAST = (By.CSS_SELECTOR, "main .toast-container .toast")
CSS_SELECTOR_ALERT = (By.CSS_SELECTOR, "main .alert-success")


def request_reset_account(selenium_driver, user):
    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    email_input = find_element(selenium_driver, CSS_SELECTOR_FORM_INPUT)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    email_input.send_keys(user.email)

    submit_button.click()

    alert = find_element(selenium_driver, CSS_SELECTOR_ALERT)

    assert alert.text == "Check the specified email to reset your account. If there is an email associated with a " \
                         "Pajelingo account, you should have received an email with a reset link."

    received_email = mail.outbox[0]
    reset_endpoint = received_email.body.split(FRONT_END_URL)[1].split("If you did not ask for a password reset,")[0]

    return reset_endpoint


def submit_reset_account_form(selenium_driver, password, confirm_password):
    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUT, 2)
    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUT[0], CSS_SELECTOR_FORM_INPUT[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    password = "" if (password is None) else password

    form_inputs[0].send_keys(password)

    if confirm_password is None:
        form_inputs[1].send_keys("")
    else:
        form_inputs[1].send_keys(password if confirm_password else get_random_string(8))

    submit_button.click()



def test_reset_account_form_rendering(live_server, selenium_driver, account):
    user, _ = account()[0]

    reset_endpoint = request_reset_account(selenium_driver, user)

    selenium_driver.get(FRONT_END_URL + reset_endpoint)

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUT, 2)
    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUT[0], CSS_SELECTOR_FORM_INPUT[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    assert len(form_inputs) == 2
    assert submit_button.text == "Submit"


@pytest.mark.parametrize(
    "password, confirm_password, feedback", [
        (None, True, "This field is required."),
        (get_too_short_password(), True, "The password must have a length between 8 and 30."),
        (get_too_long_password(), True, "The password must have a length between 8 and 30."),
        (get_password_without_letters(), True, "The password must have at least one letter."),
        (get_password_without_digits(), True, "The password must have at least one digit."),
        (get_password_without_special_characters(), True, "The password must have at least one special character."),
        (get_valid_password(), None, "This field is required."),
        (get_valid_password(), False, "The passwords do not match.")
    ]
)
def test_reset_account_form_validations(live_server, selenium_driver, account, password, confirm_password, feedback):
    user, _ = account()[0]

    reset_endpoint = request_reset_account(selenium_driver, user)

    selenium_driver.get(FRONT_END_URL + reset_endpoint)

    submit_reset_account_form(selenium_driver, password, confirm_password)

    form_validation_warnings = find_element(selenium_driver, CSS_SELECTOR_VALIDATION_WARNING)

    assert form_validation_warnings.text == feedback


def test_reset_account_wrong_url(live_server, selenium_driver, account):
    user, _ = account()[0]

    reset_endpoint = request_reset_account(selenium_driver, user)

    selenium_driver.get(FRONT_END_URL + reset_endpoint + get_random_string(1))

    password = get_valid_password()

    submit_reset_account_form(selenium_driver, password, True)

    alert_toast = find_element(selenium_driver, CSS_SELECTOR_ALERT_TOAST)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to update account. Please check the information provided."


def test_reset_account_non_active_user(live_server, selenium_driver, account):
    user, _ = account()[0]

    reset_endpoint = request_reset_account(selenium_driver, user)
    # Deactivating account
    user.is_active = False
    user.save()

    selenium_driver.get(FRONT_END_URL + reset_endpoint)

    password = get_valid_password()

    submit_reset_account_form(selenium_driver, password, True)

    alert_toast = find_element(selenium_driver, CSS_SELECTOR_ALERT_TOAST)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to update account. Please check the information provided."


def test_reset_account_already_used_link(live_server, selenium_driver, account):
    user, _ = account()[0]

    reset_endpoint = request_reset_account(selenium_driver, user)

    selenium_driver.get(FRONT_END_URL + reset_endpoint)

    password = get_valid_password()

    submit_reset_account_form(selenium_driver, password, True)

    alert = find_element(selenium_driver, CSS_SELECTOR_ALERT)

    assert alert.text == "Password successfully updated!"
    user = User.objects.filter(id=user.id, username=user.username, email=user.email).first()
    assert check_password(password, user.password)

    selenium_driver.get(FRONT_END_URL + reset_endpoint)

    password = get_valid_password()

    submit_reset_account_form(selenium_driver, password, True)

    alert_toast = find_element(selenium_driver, CSS_SELECTOR_ALERT_TOAST)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to update account. Please check the information provided."



def test_reset_account(live_server, selenium_driver, account):
    user, _ = account()[0]

    reset_endpoint = request_reset_account(selenium_driver, user)

    selenium_driver.get(FRONT_END_URL + reset_endpoint)

    password = get_valid_password()

    submit_reset_account_form(selenium_driver, password, True)

    alert = find_element(selenium_driver, CSS_SELECTOR_ALERT)

    assert alert.text == "Password successfully updated!"
    user = User.objects.filter(id=user.id, username=user.username, email=user.email).first()
    assert check_password(password, user.password)
