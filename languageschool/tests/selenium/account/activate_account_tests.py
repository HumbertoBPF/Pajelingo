from django.core import mail
from django.utils.crypto import get_random_string

from languageschool.models import User
from languageschool.tests.selenium.utils import signup_user, find_by_test_id
from languageschool.tests.utils import get_random_email, get_random_username, get_valid_password, get_random_bio
from pajelingo.settings import FRONT_END_URL

EMAIL = get_random_email()
USERNAME = get_random_username()
BIO = get_random_bio()
PASSWORD = get_valid_password()

def test_activate_account_success(live_server, selenium_driver):
    signup_user(selenium_driver, EMAIL, USERNAME, BIO, PASSWORD)
    activate_account_url = mail.outbox[0].body.split(FRONT_END_URL)[1]
    selenium_driver.get(FRONT_END_URL + activate_account_url)

    alert_success = find_by_test_id(selenium_driver, "success-alert")
    dashboard_button = find_by_test_id(selenium_driver, "dashboard-button")
    login_button = find_by_test_id(selenium_driver, "login-button")

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

    alert_danger = find_by_test_id(selenium_driver, "error-alert")
    dashboard_button = find_by_test_id(selenium_driver, "dashboard-button")
    login_button = find_by_test_id(selenium_driver, "login-button")

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

    alert_danger = find_by_test_id(selenium_driver, "error-alert")
    dashboard_button = find_by_test_id(selenium_driver, "dashboard-button")
    login_button = find_by_test_id(selenium_driver, "login-button")

    assert alert_danger.text == "Invalid token!"
    assert dashboard_button.text == "Go to dashboard"
    assert login_button.text == "Login"
