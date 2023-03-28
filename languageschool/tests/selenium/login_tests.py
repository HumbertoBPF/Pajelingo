import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_element, assert_menu
from pajelingo.settings import FRONT_END_URL

LOGIN_URL = FRONT_END_URL + "/login"
CSS_SELECTOR_INPUTS = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")
CSS_SELECTOR_VALIDATION_WARNING = (By.CSS_SELECTOR, "main form .invalid-feedback ul li")
CSS_SELECTOR_ALERT_TOAST = (By.CSS_SELECTOR, "main .toast-container .toast")


def test_login_form_rendering(live_server, selenium_driver):
    selenium_driver.get(LOGIN_URL)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_INPUTS[0], CSS_SELECTOR_INPUTS[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    assert len(form_inputs) == 2
    assert submit_button.text == "Sign in"

    assert_menu(selenium_driver)


@pytest.mark.parametrize(
    "has_username, has_password", [
        (True, False),
        (False, True),
        (False, False)
    ]
)
def test_login_form_validation(live_server, selenium_driver, has_username, has_password):
    selenium_driver.get(LOGIN_URL)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_INPUTS[0], CSS_SELECTOR_INPUTS[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    username = get_random_string(8) if has_username else ""
    password = get_random_string(8) if has_password else ""

    form_inputs[0].send_keys(username)
    form_inputs[1].send_keys(password)

    submit_button.click()

    form_validation_warnings = selenium_driver.find_elements(CSS_SELECTOR_VALIDATION_WARNING[0],
                                                             CSS_SELECTOR_VALIDATION_WARNING[1])

    username_validation_warning = form_validation_warnings[0]
    password_validation_warning = form_validation_warnings[-1]

    if not has_username:
        assert username_validation_warning.text == "This field is required."

    if not has_password:
        assert password_validation_warning.text == "This field is required."

    assert_menu(selenium_driver)


@pytest.mark.parametrize("is_correct_username", [True, False])
@pytest.mark.parametrize("is_correct_password", [True, False])
@pytest.mark.django_db
def test_login(live_server, selenium_driver, account, is_correct_username, is_correct_password):
    user, password = account()[0]

    selenium_driver.get(LOGIN_URL)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_INPUTS[0], CSS_SELECTOR_INPUTS[1])
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    username = user.username if is_correct_username else get_random_string(8)
    password = password if is_correct_password else get_random_string(8)

    form_inputs[0].send_keys(username)
    form_inputs[1].send_keys(password)

    submit_button.click()

    is_valid_login = is_correct_username and is_correct_password

    if is_valid_login:
        css_selector_carousel = (By.CSS_SELECTOR, "main .carousel")
        find_element(selenium_driver, css_selector_carousel)
    else:
        alert_toast = find_element(selenium_driver, CSS_SELECTOR_ALERT_TOAST)

        assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
        assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
               "It was not possible to log you in. Please check your credentials."

    assert_menu(selenium_driver, user if is_valid_login else None)
