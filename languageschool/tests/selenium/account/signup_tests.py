import pytest
from django.contrib.auth.hashers import check_password
from django.core import mail
from selenium.webdriver.common.by import By

from languageschool.models import User
from languageschool.tests.selenium.utils import submit_user_form, find_by_test_id
from languageschool.tests.utils import get_random_username, get_valid_password, get_random_email, \
    get_random_bio
from pajelingo.settings import FRONT_END_URL

SIGNUP_URL = f"{FRONT_END_URL}/signup"
TEST_ID_SUCCESS_ALERT = "success-alert"
TEST_ID_ERROR_TOAST = "error-toast"


@pytest.mark.django_db
def test_signup_repeated_email(live_server, selenium_driver, account):
    user, password = account()[0]

    selenium_driver.get(SIGNUP_URL)

    email = user.email
    username = get_random_username()
    bio = get_random_bio()
    password = get_valid_password()

    submit_user_form(selenium_driver, email, username, bio, password, True)

    alert_toast = find_by_test_id(selenium_driver, TEST_ID_ERROR_TOAST)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to create account. Please check the information provided."


@pytest.mark.django_db
def test_signup_repeated_username(live_server, selenium_driver, account):
    user, password = account()[0]

    selenium_driver.get(SIGNUP_URL)

    email = get_random_email()
    username = user.username
    bio = get_random_bio()
    password = get_valid_password()

    submit_user_form(selenium_driver, email, username, bio, password, True)

    alert_toast = find_by_test_id(selenium_driver, TEST_ID_ERROR_TOAST)

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

    alert_success = find_by_test_id(selenium_driver, TEST_ID_SUCCESS_ALERT)
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
    assert (f"Hi {username},\n\nPlease click on the link below to activate your Pajelingo account:\n\n{FRONT_END_URL}"
            in signup_email.body)
    assert len(signup_email.to) == 1
    assert signup_email.to[0] == email
