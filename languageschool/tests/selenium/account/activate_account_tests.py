from django.core import mail
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import User
from languageschool.tests.selenium.utils import find_element, signup_user
from languageschool.tests.utils import get_random_email, get_random_username, get_valid_password, get_random_bio
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_ALERT_SUCCESS = (By.CSS_SELECTOR, "main .alert-success")
CSS_SELECTOR_ALERT_DANGER = (By.CSS_SELECTOR, "main .alert-danger")
CSS_SELECTOR_DASHBOARD_BUTTON = (By.CSS_SELECTOR, "main .btn-primary")
CSS_SELECTOR_LOGIN_BUTTON = (By.CSS_SELECTOR, "main .btn-success")

EMAIL = get_random_email()
USERNAME = get_random_username()
BIO = get_random_bio()
PASSWORD = get_valid_password()

def test_activate_account_success(live_server, selenium_driver):
    signup_user(selenium_driver, EMAIL, USERNAME, BIO, PASSWORD)
    activate_account_url = mail.outbox[0].body.split(FRONT_END_URL)[1]
    selenium_driver.get(FRONT_END_URL + activate_account_url)

    alert_success = find_element(selenium_driver, CSS_SELECTOR_ALERT_SUCCESS)
    dashboard_button = find_element(selenium_driver, CSS_SELECTOR_DASHBOARD_BUTTON)
    login_button = find_element(selenium_driver, CSS_SELECTOR_LOGIN_BUTTON)

    assert alert_success.text == "Thank you for your email confirmation. Now you can sign in your account."
    assert User.objects.filter(
        username=USERNAME,
        email=EMAIL,
        bio=BIO,
        is_active=True
    ).exists()
    assert dashboard_button.text == "Go to dashboard"
    assert login_button.text == "Login"


def test_activate_account_invalid_url(live_server, selenium_driver):
    signup_user(selenium_driver, EMAIL, USERNAME, BIO, PASSWORD)
    activate_account_url = mail.outbox[0].body.split(FRONT_END_URL)[1]
    selenium_driver.get(FRONT_END_URL + activate_account_url + get_random_string(1))

    alert_danger = find_element(selenium_driver, CSS_SELECTOR_ALERT_DANGER)
    dashboard_button = find_element(selenium_driver, CSS_SELECTOR_DASHBOARD_BUTTON)
    login_button = find_element(selenium_driver, CSS_SELECTOR_LOGIN_BUTTON)

    assert alert_danger.text == "Invalid token!"
    assert User.objects.filter(
        username=USERNAME,
        email=EMAIL,
        bio=BIO,
        is_active=False
    ).exists()
    assert dashboard_button.text == "Go to dashboard"
    assert login_button.text == "Login"


def test_activate_account_already_active_user(live_server, selenium_driver):
    signup_user(selenium_driver, EMAIL, USERNAME, BIO, PASSWORD)

    user = User.objects.filter(
        username=USERNAME,
        email=EMAIL,
        bio=BIO,
        is_active=False
    ).first()
    user.is_active = True
    user.save()

    activate_account_url = mail.outbox[0].body.split(FRONT_END_URL)[1]
    selenium_driver.get(FRONT_END_URL + activate_account_url)

    alert_danger = find_element(selenium_driver, CSS_SELECTOR_ALERT_DANGER)
    dashboard_button = find_element(selenium_driver, CSS_SELECTOR_DASHBOARD_BUTTON)
    login_button = find_element(selenium_driver, CSS_SELECTOR_LOGIN_BUTTON)

    assert alert_danger.text == "Invalid token!"
    assert dashboard_button.text == "Go to dashboard"
    assert login_button.text == "Login"
