import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import assert_menu, authenticate
from languageschool.tests.utils import get_random_username, get_valid_password
from languageschool.views.account import LOGIN_ERROR


class TestsLoginSelenium:
    @pytest.mark.django_db
    def test_login_form_rendering(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url + reverse("login"))

        inputs = selenium_driver.find_elements(By.CSS_SELECTOR, "form .form-control")
        username_input = inputs[0]
        password_input = inputs[1]
        submits_button = selenium_driver.find_elements(By.CSS_SELECTOR, "form div .btn-success")

        assert len(inputs) == 2
        assert username_input.get_attribute("placeholder") == "Username"
        assert password_input.get_attribute("placeholder") == "Password"
        assert len(submits_button) == 1
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_successful_login_attempt(self, live_server, selenium_driver, account):
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        assert selenium_driver.current_url == live_server.url + reverse("index")
        assert_menu(selenium_driver, user=user)

    @pytest.mark.django_db
    def test_failed_login_attempt(self, live_server, selenium_driver, account):
        account()
        authenticate(live_server, selenium_driver, get_random_username(), get_valid_password())
        alert_danger = selenium_driver.find_element(By.CLASS_NAME, "alert-danger")
        assert alert_danger.text == LOGIN_ERROR
        assert_menu(selenium_driver)
