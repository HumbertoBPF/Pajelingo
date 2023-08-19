import pytest
from django.core import mail
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_by_test_id
from languageschool.tests.utils import get_random_email
from pajelingo.settings import FRONT_END_URL

REQUEST_RESET_ACCOUNT_URL = f"{FRONT_END_URL}/request-reset-account"


def test_request_reset_account_email_does_not_match_account(live_server, selenium_driver):
    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    email_input = find_by_test_id(selenium_driver, "email-input").find_element(By.CSS_SELECTOR, "input")
    email_input.send_keys(get_random_email())

    submit_button = find_by_test_id(selenium_driver, "submit-button")
    submit_button.click()

    alert = find_by_test_id(selenium_driver, "successful-request-alert")

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

    email_input = find_by_test_id(selenium_driver, "email-input").find_element(By.CSS_SELECTOR, "input")
    email_input.send_keys(get_random_email())

    submit_button = find_by_test_id(selenium_driver, "submit-button")
    submit_button.click()

    alert = find_by_test_id(selenium_driver, "successful-request-alert")

    assert alert.text == "Check the specified email to reset your account. If there is an email associated with a " \
                         "Pajelingo account, you should have received an email with a reset link."
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_request_reset_account(live_server, selenium_driver, account):
    user, _ = account()[0]

    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    email_input = find_by_test_id(selenium_driver, "email-input").find_element(By.CSS_SELECTOR, "input")
    email_input.send_keys(user.email)

    submit_button = find_by_test_id(selenium_driver, "submit-button")
    submit_button.click()

    alert = find_by_test_id(selenium_driver, "successful-request-alert")

    assert alert.text == "Check the specified email to reset your account. If there is an email associated with a " \
                         "Pajelingo account, you should have received an email with a reset link."
    assert len(mail.outbox) == 1
    received_email = mail.outbox[0]
    assert received_email.subject == "Pajelingo account reset"
    assert f"Hi {user.username},\n\nA password reset was requested to your Pajelingo account. " \
           f"If it was you who request it, please access the following link:\n\n" \
           f"{FRONT_END_URL}" in received_email.body
    assert len(received_email.to) == 1
    assert received_email.to[0] == user.email
