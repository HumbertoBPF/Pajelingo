import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import assert_menu, find_by_test_id
from pajelingo.settings import FRONT_END_URL

LOGIN_URL = f"{FRONT_END_URL}/login"
TEST_ID_USERNAME_INPUT = "username-input"
TEST_ID_PASSWORD_INPUT = "password-input"
TEST_ID_SUBMIT_BUTTON = "login-button"
TEST_ID_CAROUSEL = "carousel"
TEST_ID_ERROR_TOAST = "toast-error"


@pytest.mark.django_db
def test_failed_login(live_server, selenium_driver):
    selenium_driver.get(LOGIN_URL)

    username_input = find_by_test_id(selenium_driver, TEST_ID_USERNAME_INPUT).find_element(By.CSS_SELECTOR, "input")
    username_input.send_keys(get_random_string(8))

    password_input = find_by_test_id(selenium_driver, TEST_ID_PASSWORD_INPUT).find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(get_random_string(8))

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    alert_toast = find_by_test_id(selenium_driver, TEST_ID_ERROR_TOAST)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to log you in. Please check your credentials."

    assert_menu(selenium_driver, None)


@pytest.mark.django_db
def test_successful_login(live_server, selenium_driver, account):
    user, password = account()[0]

    selenium_driver.get(LOGIN_URL)

    username_input = find_by_test_id(selenium_driver, TEST_ID_USERNAME_INPUT).find_element(By.CSS_SELECTOR, "input")
    username_input.send_keys(user.username)

    password_input = find_by_test_id(selenium_driver, TEST_ID_PASSWORD_INPUT).find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(password)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    find_by_test_id(selenium_driver, TEST_ID_CAROUSEL)
    assert_menu(selenium_driver, user)
