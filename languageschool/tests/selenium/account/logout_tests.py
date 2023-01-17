import pytest
from django.urls import reverse

from languageschool.tests.selenium.utils import authenticate, assert_menu


class TestsLogoutSelenium:
    @pytest.mark.django_db
    def test_logout_with_authenticated_user(self, live_server, selenium_driver, account):
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("logout"))
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_logout_without_authenticated_user(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url + reverse("logout"))
        assert_menu(selenium_driver)
