import pytest
from django.core import mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import assert_menu, get_form_error_message, WARNING_REQUIRED_FIELD_HTML, \
    authenticate
from languageschool.tests.utils import get_random_email, get_valid_password, get_too_short_password, \
    get_too_long_password, get_password_without_letters, get_password_without_digits, \
    get_password_without_special_characters
from pajelingo import settings
from pajelingo.validators.auth_password_validators import ERROR_LENGTH_PASSWORD, ERROR_LETTER_PASSWORD, \
    ERROR_DIGIT_PASSWORD, ERROR_SPECIAL_CHARACTER_PASSWORD


class TestResetAccountSelenium:
    def request_reset_account(self, live_server, selenium_driver, email):
        """
        Requests the reset of an account with the specified email.

        :param live_server: live server fixture
        :param selenium_driver: Selenium web driver
        :param email: email address to be input
        """
        selenium_driver.get(live_server.url + reverse("login"))

        selenium_driver.find_element(By.ID, "reset_account_link").click()

        selenium_driver.find_element(By.ID, "id_email").send_keys(email)
        selenium_driver.find_element(By.ID, "submitRequestResetAccountFormButton").click()


    def get_reset_account_link(self, live_server, selenium_driver, email):
        """
        Gets the reset account link of the specified user.

        :param live_server: live server fixture
        :param selenium_driver: Selenium web driver
        :param email: valid email of the account that must be reset

        :return: link for resetting account.
        """
        self.request_reset_account(live_server, selenium_driver, email)

        assert len(mail.outbox) == 1

        return "http" + mail.outbox[0].body.split("http")[1].split("\n\nIf you did not ask")[0]

    @pytest.mark.django_db
    def test_request_reset_account_form_rendering(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url+reverse("login"))

        selenium_driver.find_element(By.ID, "reset_account_link").click()

        email_labels = selenium_driver.find_elements(By.ID, "id_email_label")
        email_inputs = selenium_driver.find_elements(By.ID, "id_email")
        submit_buttons = selenium_driver.find_elements(By.ID, "submitRequestResetAccountFormButton")

        assert len(email_labels) == 1
        assert len(email_inputs) == 1
        assert len(submit_buttons) == 1
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_request_reset_account_no_email(self, live_server, selenium_driver):
        selenium_driver.get(live_server.url + reverse("login"))

        selenium_driver.find_element(By.ID, "reset_account_link").click()

        selenium_driver.find_element(By.ID, "submitRequestResetAccountFormButton").click()

        email_warning = get_form_error_message(selenium_driver, "id_email")

        assert email_warning == WARNING_REQUIRED_FIELD_HTML
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_request_reset_account_invalid_email(self, live_server, selenium_driver):
        self.request_reset_account(live_server, selenium_driver, get_random_email())

        alert_successes = selenium_driver.find_elements(By.CLASS_NAME, "alert-success")

        assert len(alert_successes) == 1
        assert len(mail.outbox) == 0
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_request_reset_account_valid_email(self, live_server, selenium_driver, account):
        user, _ = account()[0]
        self.request_reset_account(live_server, selenium_driver, user.email)

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
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_reset_account_form_rendering(self, live_server, selenium_driver, account):
        user, _ = account()[0]
        selenium_driver.get(self.get_reset_account_link(live_server, selenium_driver, user.email))

        password_labels = selenium_driver.find_elements(By.ID, "id_new_password1_label")
        password_inputs = selenium_driver.find_elements(By.ID, "id_new_password1")
        confirmation_password_labels = selenium_driver.find_elements(By.ID, "id_new_password2_label")
        confirmation_input_labels = selenium_driver.find_elements(By.ID, "id_new_password2_label")
        submit_buttons = selenium_driver.find_elements(By.ID, "submitResetAccountFormButton")

        assert len(password_labels) == 1
        assert len(password_inputs) == 1
        assert len(confirmation_password_labels) == 1
        assert len(confirmation_input_labels) == 1
        assert len(submit_buttons) == 1
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_reset_account_invalid_link(self, live_server, selenium_driver, account):
        user, _ = account()[0]
        selenium_driver.get(self.get_reset_account_link(live_server, selenium_driver, user.email)+get_random_string(5))

        alert_dangers = selenium_driver.find_elements(By.CLASS_NAME, "alert-danger")

        assert len(alert_dangers) == 1
        assert alert_dangers[0].text == "Invalid token!"
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_reset_account_different_passwords(self, live_server, selenium_driver, account):
        user, password = account()[0]
        selenium_driver.get(self.get_reset_account_link(live_server, selenium_driver, user.email))

        new_password = get_valid_password()
        diff_password = get_valid_password()

        while new_password == diff_password:
            diff_password = get_valid_password()

        selenium_driver.find_element(By.ID, "id_new_password1").send_keys(new_password)
        selenium_driver.find_element(By.ID, "id_new_password2").send_keys(diff_password)
        selenium_driver.find_element(By.ID, "submitResetAccountFormButton").click()

        alert_dangers = selenium_driver.find_elements(By.CLASS_NAME, "alert-danger")

        assert len(alert_dangers) == 1
        assert alert_dangers[0].text == "The two password fields didn’t match."
        assert_menu(selenium_driver, False)
        # Verifies that the user credentials keep the same
        authenticate(live_server, selenium_driver, user.username, password)

        greeting = selenium_driver.find_element(By.ID, "greeting")

        assert greeting.text == "Welcome back, {}".format(user.username)

    @pytest.mark.parametrize(
        "new_password, error_message", [
            (get_too_short_password(), ERROR_LENGTH_PASSWORD),
            (get_too_long_password(), ERROR_LENGTH_PASSWORD),
            (get_password_without_letters(), ERROR_LETTER_PASSWORD),
            (get_password_without_digits(), ERROR_DIGIT_PASSWORD),
            (get_password_without_special_characters(), ERROR_SPECIAL_CHARACTER_PASSWORD)
        ]
    )
    @pytest.mark.django_db
    def test_reset_account_invalid_password(self, live_server, selenium_driver, account, new_password, error_message):
        user, _ = account()[0]
        selenium_driver.get(self.get_reset_account_link(live_server, selenium_driver, user.email))

        selenium_driver.find_element(By.ID, "id_new_password1").send_keys(new_password)
        selenium_driver.find_element(By.ID, "id_new_password2").send_keys(new_password)
        selenium_driver.find_element(By.ID, "submitResetAccountFormButton").click()

        alert_dangers = selenium_driver.find_elements(By.CLASS_NAME, "alert-danger")

        assert len(alert_dangers) == 1
        assert error_message in alert_dangers[0].text
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_reset_account_same_passwords(self, live_server, selenium_driver, account):
        user, _ = account()[0]
        selenium_driver.get(self.get_reset_account_link(live_server, selenium_driver, user.email))

        new_password = get_valid_password()

        selenium_driver.find_element(By.ID, "id_new_password1").send_keys(new_password)
        selenium_driver.find_element(By.ID, "id_new_password2").send_keys(new_password)
        selenium_driver.find_element(By.ID, "submitResetAccountFormButton").click()

        alert_successes = selenium_driver.find_elements(By.CLASS_NAME, "alert-success")

        assert len(alert_successes) == 1
        assert alert_successes[0].text == "Password successfully updated!"
        assert_menu(selenium_driver, False)
        # Verifies if the user credentials changed
        authenticate(live_server, selenium_driver, user.username, new_password)

        greeting = selenium_driver.find_element(By.ID, "greeting")

        assert greeting.text == "Welcome back, {}".format(user.username)
