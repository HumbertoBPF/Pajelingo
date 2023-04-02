import pytest
from django.core import mail
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_element
from languageschool.tests.utils import get_random_email
from pajelingo.settings import FRONT_END_URL

REQUEST_RESET_ACCOUNT_URL = FRONT_END_URL + "/request-reset-account"
CSS_SELECTOR_EMAIL_INPUT = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")
CSS_SELECTOR_VALIDATION_WARNING = (By.CSS_SELECTOR, "main form .invalid-feedback ul li")
CSS_SELECTOR_ALERT = (By.CSS_SELECTOR, "main .alert-success")


def test_request_reset_account_form_display(live_server, selenium_driver):
    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    find_element(selenium_driver, CSS_SELECTOR_EMAIL_INPUT)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    assert submit_button.text == "Reset password"


@pytest.mark.parametrize(
    "email, feedback", [
        (None, "This field is required."),
        (get_random_string(8), "Enter a valid email address.")
    ]
)
def test_request_reset_account_form_validation(live_server, selenium_driver, email, feedback):
    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    email_input = find_element(selenium_driver, CSS_SELECTOR_EMAIL_INPUT)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    email = "" if (email is None) else email

    email_input.send_keys(email)

    submit_button.click()

    validation_warning = find_element(selenium_driver, CSS_SELECTOR_VALIDATION_WARNING)

    assert validation_warning.text == feedback


def test_request_reset_account_email_does_not_match_account(live_server, selenium_driver):
    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    email_input = find_element(selenium_driver, CSS_SELECTOR_EMAIL_INPUT)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    email_input.send_keys(get_random_email())

    submit_button.click()

    alert = find_element(selenium_driver, CSS_SELECTOR_ALERT)

    assert alert.text == "Check the specified email to reset your account. If there is an email associated with a " \
                         "Pajelingo account, you should have received an email with a reset link."
    assert len(mail.outbox) == 0


def test_request_reset_account_non_active_user(live_server, selenium_driver, account):
    """
    Tests that no activation email is sent if the matched account is not active.
    """
    user, _ = account()[0]
    user.is_active = False
    user.save()

    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    email_input = find_element(selenium_driver, CSS_SELECTOR_EMAIL_INPUT)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    email_input.send_keys(get_random_email())

    submit_button.click()

    alert = find_element(selenium_driver, CSS_SELECTOR_ALERT)

    assert alert.text == "Check the specified email to reset your account. If there is an email associated with a " \
                         "Pajelingo account, you should have received an email with a reset link."
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_request_reset_account(live_server, selenium_driver, account):
    user, _ = account()[0]

    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    email_input = find_element(selenium_driver, CSS_SELECTOR_EMAIL_INPUT)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    email_input.send_keys(user.email)

    submit_button.click()

    alert = find_element(selenium_driver, CSS_SELECTOR_ALERT)

    assert alert.text == "Check the specified email to reset your account. If there is an email associated with a " \
                         "Pajelingo account, you should have received an email with a reset link."
    assert len(mail.outbox) == 1
    received_email = mail.outbox[0]
    assert received_email.subject == "Pajelingo account reset"
    assert "Hi {},\n\nA password reset was requested to your Pajelingo account. " \
           "If it was you who request it, please access the following link:\n\n" \
           "{}".format(user.username, FRONT_END_URL) in received_email.body
    assert len(received_email.to) == 1
    assert received_email.to[0] == user.email
