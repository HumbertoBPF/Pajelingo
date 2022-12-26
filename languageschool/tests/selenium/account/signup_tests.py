import random

import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.db.models import Q
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import AppUser
from languageschool.tests.selenium.utils import assert_menu, WARNING_REQUIRED_FIELD_HTML, WARNING_EMAIL_WITH_SPACE_HTML, \
    WARNING_REQUIRED_EMAIL_FIREFOX_HTML, submit_form_user, get_form_error_message
from languageschool.tests.utils import get_valid_password, get_random_email, get_random_username, \
    get_too_short_password, get_too_long_password, get_password_without_letters, get_password_without_digits, \
    get_password_without_special_characters
from languageschool.validation import ERROR_SPACE_IN_USERNAME, ERROR_LENGTH_PASSWORD, ERROR_NOT_CONFIRMED_PASSWORD, \
    ERROR_NOT_AVAILABLE_EMAIL, ERROR_NOT_AVAILABLE_USERNAME, ERROR_SPECIAL_CHARACTER_PASSWORD, ERROR_DIGIT_PASSWORD, \
    ERROR_LETTER_PASSWORD
from languageschool.views.account import SUCCESSFUL_SIGN_UP, SIGN_UP_SUBJECT, SIGN_UP_MESSAGE, SUCCESSFUL_ACTIVATION, \
    ERROR_ACTIVATION
from pajelingo import settings


class TestSignupSelenium:
    def successful_signup(self, live_server, selenium_driver):
        """
        Performs a successful signup with random credentials.

        :param live_server: live server Django pytest fixture
        :param selenium_driver: Selenium web driver

        :return: tuple with the random email and the random username.
        """
        selenium_driver.get(live_server.url + reverse("signup"))

        email = get_random_email()
        username = get_random_username()
        password = get_valid_password()

        submit_form_user(selenium_driver, email, username, password, password)

        return email, username

    @pytest.mark.django_db
    def test_signup_form_rendering(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url+reverse("signup"))

        inputs_email = selenium_driver.find_elements(By.ID, "inputEmail")
        inputs_username = selenium_driver.find_elements(By.ID, "inputUsername")
        inputs_password = selenium_driver.find_elements(By.ID, "inputPassword")
        inputs_password_confirmation = selenium_driver.find_elements(By.ID, "inputPasswordConf")
        submit_buttons_form = selenium_driver.find_elements(By.ID, "submitButtonSignup")

        assert len(inputs_email) == 1
        assert len(inputs_username) == 1
        assert len(inputs_password) == 1
        assert len(inputs_password_confirmation) == 1
        assert len(submit_buttons_form) == 1
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_signup(self, live_server, selenium_driver):
        email, username = self.successful_signup(live_server, selenium_driver)

        alert_success = selenium_driver.find_element(By.CLASS_NAME, "alert-success")

        assert alert_success.text == SUCCESSFUL_SIGN_UP
        assert User.objects.filter(username=username, email=email, is_active=False).exists()
        assert AppUser.objects.filter(user__username=username, user__email=email, user__is_active=False).exists()
        # Checking that the activation email was received
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == SIGN_UP_SUBJECT
        assert SIGN_UP_MESSAGE.split("{}")[1] in mail.outbox[0].body
        assert mail.outbox[0].to == [email]
        assert mail.outbox[0].from_email == settings.EMAIL_FROM

        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_activate_account(self, live_server, selenium_driver):
        email, username = self.successful_signup(live_server, selenium_driver)

        activation_link = "http://" + mail.outbox[0].body.split("http://")[1]

        selenium_driver.get(activation_link)

        alert_success = selenium_driver.find_element(By.CLASS_NAME, "alert-success")

        assert alert_success.text == SUCCESSFUL_ACTIVATION
        assert User.objects.filter(username=username, email=email, is_active=True).exists()

    @pytest.mark.django_db
    def test_activate_account_invalid_token(self, live_server, selenium_driver):
        email, username = self.successful_signup(live_server, selenium_driver)

        activation_link = "http://" + mail.outbox[0].body.split("http://")[1] + get_random_string(5)

        selenium_driver.get(activation_link)

        alert_danger = selenium_driver.find_element(By.CLASS_NAME, "alert-danger")

        assert alert_danger.text == ERROR_ACTIVATION
        assert User.objects.filter(username=username, email=email, is_active=False).exists()

    @pytest.mark.parametrize(
        "email, username, password, is_password_confirmed, field, accepted_messages", [
            (get_random_email(), get_random_username(), "", True, "inputPassword", [WARNING_REQUIRED_FIELD_HTML]),
            (get_random_email(), "", get_valid_password(), True, "inputUsername", [WARNING_REQUIRED_FIELD_HTML]),
            ("", get_random_username(), get_valid_password(), True, "inputEmail", [WARNING_REQUIRED_FIELD_HTML]),
            (get_random_string(random.randint(1, 10))+" "+get_random_email(), get_random_username(), get_valid_password(), True, "inputEmail", [WARNING_EMAIL_WITH_SPACE_HTML, WARNING_REQUIRED_EMAIL_FIREFOX_HTML]),
            (get_random_email(), get_random_string(random.randint(1, 10))+" "+get_random_username(), get_valid_password(), True, "alert-danger", [ERROR_SPACE_IN_USERNAME]),
            (get_random_email(), get_random_username(), get_too_short_password(), True, "alert-danger", [ERROR_LENGTH_PASSWORD]),
            (get_random_email(), get_random_username(), get_too_long_password(), True, "alert-danger", [ERROR_LENGTH_PASSWORD]),
            (get_random_email(), get_random_username(), get_password_without_letters(), True, "alert-danger", [ERROR_LETTER_PASSWORD]),
            (get_random_email(), get_random_username(), get_password_without_digits(), True, "alert-danger", [ERROR_DIGIT_PASSWORD]),
            (get_random_email(), get_random_username(), get_password_without_special_characters(), True, "alert-danger", [ERROR_SPECIAL_CHARACTER_PASSWORD]),
            (get_random_email(), get_random_username(), get_valid_password(), False, "alert-danger", [ERROR_NOT_CONFIRMED_PASSWORD])
        ]
    )
    @pytest.mark.django_db
    def test_signup_form_error(self, live_server, selenium_driver, email, username, password, is_password_confirmed, field, accepted_messages):
        selenium_driver.get(live_server.url + reverse("signup"))

        confirmation_password = password if is_password_confirmed else get_valid_password()

        submit_form_user(selenium_driver, email, username, password, confirmation_password)

        is_valid_message = False

        for message in accepted_messages:
            is_valid_message = is_valid_message or (get_form_error_message(selenium_driver, field) == message)

        assert is_valid_message
        assert not User.objects.filter(username=username, email=email).exists()
        assert not AppUser.objects.filter(user__username=username, user__email=email).exists()
        assert_menu(selenium_driver, False)

    @pytest.mark.parametrize(
        "is_repeated_email, is_repeated_username", [
            (True, True),
            (True, False),
            (False, True)
        ]
    )
    @pytest.mark.django_db
    def test_signup_form_error_not_available_credentials(self, live_server, selenium_driver, account, is_repeated_email, is_repeated_username):
        user, _ = account()[0]
        selenium_driver.get(live_server.url + reverse("signup"))

        password = get_valid_password()

        email = user.email if is_repeated_email else get_random_email()
        username = user.username if is_repeated_username else get_random_username()

        submit_form_user(selenium_driver, email, username, password, password)

        alert_danger = selenium_driver.find_element(By.CLASS_NAME, "alert-danger")

        if is_repeated_email:
            assert alert_danger.text == ERROR_NOT_AVAILABLE_EMAIL
        elif is_repeated_username:
            assert alert_danger.text == ERROR_NOT_AVAILABLE_USERNAME
        # Verifies if there is a user other than the fixture user with the specified credentials
        assert not User.objects.filter(username=username, email=email).filter(~Q(id=user.id)).exists()
        assert not AppUser.objects.filter(user__username=username, user__email=email).filter(~Q(user__id=user.id)).exists()
        assert_menu(selenium_driver, False)
