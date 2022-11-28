import random

import pytest
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import AppUser
from languageschool.tests.selenium.utils import assert_menu, WARNING_REQUIRED_FIELD_HTML, WARNING_EMAIL_WITH_SPACE_HTML, \
    WARNING_REQUIRED_EMAIL_FIREFOX_HTML, submit_form_user, get_form_error_message
from languageschool.tests.utils import get_valid_password, get_random_email, get_random_username
from languageschool.validation import ERROR_SPACE_IN_USERNAME, ERROR_LENGTH_PASSWORD, ERROR_NOT_CONFIRMED_PASSWORD, \
    ERROR_NOT_AVAILABLE_EMAIL, ERROR_NOT_AVAILABLE_USERNAME
from languageschool.views.account import SUCCESSFUL_SIGN_UP


class TestSignupSelenium:
    @pytest.mark.django_db
    def test_signup_form_rendering(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url+reverse("account-sign-in"))

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
        selenium_driver.get(live_server.url + reverse("account-sign-in"))

        email = get_random_email()
        username = get_random_username()
        password = get_valid_password()

        submit_form_user(selenium_driver, email, username, password, password)

        alert_success = selenium_driver.find_element(By.CLASS_NAME, "alert-success")

        assert alert_success.text == SUCCESSFUL_SIGN_UP
        assert User.objects.filter(username=username, email=email).exists()
        assert AppUser.objects.filter(user__username=username, user__email=email).exists()
        assert_menu(selenium_driver, False)

    @pytest.mark.parametrize(
        "email, username, password, is_password_confirmed, field, accepted_messages", [
            (get_random_email(), get_random_username(), "", True, "inputPassword", [WARNING_REQUIRED_FIELD_HTML]),
            (get_random_email(), "", get_valid_password(), True, "inputUsername", [WARNING_REQUIRED_FIELD_HTML]),
            ("", get_random_username(), get_valid_password(), True, "inputEmail", [WARNING_REQUIRED_FIELD_HTML]),
            (get_random_string(random.randint(1, 10))+" "+get_random_email(), get_random_username(), get_valid_password(), True, "inputEmail", [WARNING_EMAIL_WITH_SPACE_HTML, WARNING_REQUIRED_EMAIL_FIREFOX_HTML]),
            (get_random_email(), get_random_string(random.randint(1, 10))+" "+get_random_username(), get_valid_password(), True, "alert-danger", [ERROR_SPACE_IN_USERNAME]),
            (get_random_email(), get_random_username(), get_random_string(random.randint(1, 7)), True, "alert-danger", [ERROR_LENGTH_PASSWORD]),
            (get_random_email(), get_random_username(), get_random_string(random.randint(31, 50)), True, "alert-danger", [ERROR_LENGTH_PASSWORD]),
            (get_random_email(), get_random_username(), get_valid_password(), False, "alert-danger", [ERROR_NOT_CONFIRMED_PASSWORD])
        ]
    )
    @pytest.mark.django_db
    def test_signup_form_error(self, live_server, selenium_driver, email, username, password, is_password_confirmed, field, accepted_messages):
        selenium_driver.get(live_server.url + reverse("account-sign-in"))

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
        selenium_driver.get(live_server.url + reverse("account-sign-in"))

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
