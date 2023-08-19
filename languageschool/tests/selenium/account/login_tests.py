import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_by_test_id
from pajelingo.settings import FRONT_END_URL

LOGIN_URL = f"{FRONT_END_URL}/login"


@pytest.mark.django_db
def test_failed_login(live_server, selenium_driver):
    selenium_driver.get(LOGIN_URL)

    username_input = find_by_test_id(selenium_driver, "username-input").find_element(By.CSS_SELECTOR, "input")
    username_input.send_keys(get_random_string(8))

    password_input = find_by_test_id(selenium_driver, "password-input").find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(get_random_string(8))

    submit_button = find_by_test_id(selenium_driver, "login-button")
    submit_button.click()

    alert_toast = find_by_test_id(selenium_driver, "toast-error")

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to log you in. Please check your credentials."


@pytest.mark.django_db
def test_successful_login(live_server, selenium_driver, account):
    user, password = account()[0]

    selenium_driver.get(LOGIN_URL)

    username_input = find_by_test_id(selenium_driver, "username-input").find_element(By.CSS_SELECTOR, "input")
    username_input.send_keys(user.username)

    password_input = find_by_test_id(selenium_driver, "password-input").find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(password)

    submit_button = find_by_test_id(selenium_driver, "login-button")
    submit_button.click()

    find_by_test_id(selenium_driver, "carousel")
