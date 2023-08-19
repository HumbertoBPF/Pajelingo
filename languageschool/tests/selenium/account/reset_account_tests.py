from django.contrib.auth.hashers import check_password
from django.core import mail
from rest_framework.authtoken.admin import User
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_by_test_id
from languageschool.tests.utils import get_valid_password
from pajelingo.settings import FRONT_END_URL

REQUEST_RESET_ACCOUNT_URL = f"{FRONT_END_URL}/request-reset-account"


def request_reset_account(selenium_driver, user):
    selenium_driver.get(REQUEST_RESET_ACCOUNT_URL)

    email_input = find_by_test_id(selenium_driver, "email-input").find_element(By.CSS_SELECTOR, "input")
    email_input.send_keys(user.email)

    submit_button = find_by_test_id(selenium_driver, "submit-button")
    submit_button.click()

    find_by_test_id(selenium_driver, "successful-request-alert")

    received_email = mail.outbox[0]
    reset_endpoint = received_email.body.split(FRONT_END_URL)[1].split("If you did not ask for a password reset,")[0]

    return reset_endpoint


def test_reset_account(live_server, selenium_driver, account):
    user, _ = account()[0]

    reset_endpoint = request_reset_account(selenium_driver, user)

    selenium_driver.get(FRONT_END_URL + reset_endpoint)

    password = get_valid_password()

    password_input = find_by_test_id(selenium_driver, "password-input").find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(password)

    confirm_password_input = find_by_test_id(selenium_driver, "confirm-password-input") \
        .find_element(By.CSS_SELECTOR, "input")
    confirm_password_input.send_keys(password)

    submit_button = find_by_test_id(selenium_driver, "submit-button")
    submit_button.click()

    alert = find_by_test_id(selenium_driver, "successful-reset-alert")
    assert alert.text == "Password successfully updated!"

    user = User.objects.get(id=user.id)
    assert check_password(password, user.password)
