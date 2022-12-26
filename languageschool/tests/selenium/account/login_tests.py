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

        inputs_username = selenium_driver.find_elements(By.ID, "inputUsername")
        inputs_password = selenium_driver.find_elements(By.ID, "inputPassword")
        submits_button = selenium_driver.find_elements(By.ID, "submitLoginFormButton")

        assert len(inputs_username) == 1
        assert len(inputs_password) == 1
        assert len(submits_button) == 1
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_successful_login_attempt(self, live_server, selenium_driver, account):
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        greeting = selenium_driver.find_element(By.ID, "greeting")
        assert selenium_driver.current_url == live_server.url + reverse("index")
        assert greeting.text == "Welcome back, {}".format(user.username)
        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_failed_login_attempt(self, live_server, selenium_driver, account):
        account()
        authenticate(live_server, selenium_driver, get_random_username(), get_valid_password())
        alert_danger = selenium_driver.find_element(By.CLASS_NAME, "alert-danger")
        assert alert_danger.text == LOGIN_ERROR
        assert_menu(selenium_driver, False)
