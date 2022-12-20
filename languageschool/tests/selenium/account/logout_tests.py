import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import authenticate, assert_menu


class TestsLogoutSelenium:
    @pytest.mark.django_db
    def test_logout_with_authenticated_user(self, live_server, selenium_driver, account):
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-logout"))
        greetings = selenium_driver.find_elements(By.ID, "greeting")

        assert len(greetings) == 0
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_logout_without_authenticated_user(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url + reverse("account-logout"))
        greetings = selenium_driver.find_elements(By.ID, "greeting")

        assert len(greetings) == 0
        assert_menu(selenium_driver, False)

    def new_function(self):
        print("Hello")