import random
import string

import pytest
from django.core import mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import assert_menu, request_reset_account_via_website, get_form_error
from languageschool.tests.utils import get_random_email
from pajelingo import settings
from pajelingo.validators.validators import ERROR_REQUIRED_FIELD, ERROR_EMAIL_FORMAT


class TestRequestResetAccountSelenium:
    def request_reset_account(self, live_server, selenium_driver, email, expected_error, is_server_side):
        selenium_driver.get(live_server.url + reverse("login"))

        selenium_driver.find_element(By.ID, "reset_account_link").click()

        selenium_driver.find_element(By.CSS_SELECTOR, "form .form-floating:nth-child(2) .form-control").send_keys(email)

        if is_server_side:
            selenium_driver.find_element(By.CSS_SELECTOR, "form .btn-success").click()

        assert get_form_error(selenium_driver, 1) == expected_error
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_request_reset_account_form_rendering(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url+reverse("login"))

        selenium_driver.find_element(By.ID, "reset_account_link").click()

        email_inputs = selenium_driver.find_elements(By.ID, "id_email")
        submit_buttons = selenium_driver.find_elements(By.CSS_SELECTOR, "form .btn-success")

        assert len(email_inputs) == 1
        assert len(submit_buttons) == 1
        assert_menu(selenium_driver)

    @pytest.mark.parametrize(
        "email, expected_error", [
            ("", ERROR_REQUIRED_FIELD),
            (get_random_string(random.randint(1, 50), string.ascii_letters), ERROR_EMAIL_FORMAT)
        ]
    )
    @pytest.mark.django_db
    def test_request_reset_account_client_side_validation(self, live_server, selenium_driver, email, expected_error):
        self.request_reset_account(live_server, selenium_driver, email, expected_error, False)

    @pytest.mark.parametrize(
        "email, expected_error", [
            ("", ERROR_REQUIRED_FIELD),
            (get_random_string(random.randint(1, 50), string.ascii_letters), ERROR_EMAIL_FORMAT)
        ]
    )
    @pytest.mark.django_db
    def test_request_reset_account_server_side_validation(self, live_server, selenium_driver, email, expected_error):
        self.request_reset_account(live_server, selenium_driver, email, expected_error, True)

    @pytest.mark.django_db
    def test_request_reset_account_invalid_email(self, live_server, selenium_driver):
        request_reset_account_via_website(live_server, selenium_driver, get_random_email())

        alert_successes = selenium_driver.find_elements(By.CLASS_NAME, "alert-success")

        assert len(alert_successes) == 1
        assert len(mail.outbox) == 0
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_request_reset_account_valid_email(self, live_server, selenium_driver, account):
        user, _ = account()[0]
        request_reset_account_via_website(live_server, selenium_driver, user.email)

        alert_successes = selenium_driver.find_elements(By.CLASS_NAME, "alert-success")
        starting_text = "Hi {},\n\nA password reset was requested to your Pajelingo account. If it was " \
                        "you who request it, please access the following link:".format(user.username)
        ending_text = "If you did not ask for a password reset, please ignore this email."

        assert len(alert_successes) == 1
        assert len(mail.outbox) == 1
        assert mail.outbox[0].from_email == settings.EMAIL_FROM
        assert mail.outbox[0].to == [user.email]
        assert mail.outbox[0].subject == "Pajelingo - reset account"
        assert mail.outbox[0].body.startswith(starting_text)
        assert mail.outbox[0].body.endswith(ending_text)
        assert_menu(selenium_driver)
