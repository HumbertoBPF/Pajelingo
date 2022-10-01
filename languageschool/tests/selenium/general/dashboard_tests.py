import pytest
from django.urls import reverse

from languageschool.tests.selenium.utils import assert_menu


class TestDashboardSelenium:
    @pytest.mark.django_db
    def test_dashboard(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url+reverse("index"))
        assert_menu(selenium_driver, False)
