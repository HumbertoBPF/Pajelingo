import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import assert_menu, authenticate, request_reset_account_via_website, \
    get_reset_account_link, get_form_error
from languageschool.tests.utils import get_valid_password, get_too_short_password, \
    get_too_long_password, get_password_without_letters, get_password_without_digits, \
    get_password_without_special_characters
from pajelingo.validators.auth_password_validators import ERROR_LENGTH_PASSWORD, ERROR_LETTER_PASSWORD, \
    ERROR_DIGIT_PASSWORD, ERROR_SPECIAL_CHARACTER_PASSWORD, ALL_PASSWORD_ERRORS
from pajelingo.validators.validators import ERROR_NOT_CONFIRMED_PASSWORD, ERROR_REQUIRED_FIELD


class TestResetAccountSelenium:
    def request_reset_account_via_api(self, api_client, email):
        """
        Requests the reset of an account with the specified email via Pajelingo's API.

        :param api_client: Django's REST Framework client fixture
        :param email: email address to be input
        """
        url = reverse('request-reset-account-api')
        response = api_client.post(url, {"email": email})

        assert response.status_code == status.HTTP_200_OK

    def fill_reset_password_form(self, live_server, selenium_driver, new_password, new_password_confirmation):
        """
        Accesses and fills the reset form with the specified data (password and its confirmation).

        :param live_server: live server fixture
        :param selenium_driver: Selenium web driver
        :param new_password: new password for the account
        :type new_password: str
        :param new_password_confirmation: password confirmation
        :type new_password_confirmation: str
        """
        reset_link = get_reset_account_link().replace("http://testserver", live_server.url)
        selenium_driver.get(reset_link)

        selenium_driver.find_element(By.ID, "id_new_password1").send_keys(new_password)
        selenium_driver.find_element(By.ID, "id_new_password2").send_keys(new_password_confirmation)

    def submit_reset_password_form(self, live_server, selenium_driver, new_password, new_password_confirmation):
        """
        Submits the reset form with the specified data (password and its confirmation).

        :param live_server: live server fixture
        :param selenium_driver: Selenium web driver
        :param new_password: new password for the account
        :type new_password: str
        :param new_password_confirmation: password confirmation
        :type new_password_confirmation: str
        """
        self.fill_reset_password_form(live_server, selenium_driver, new_password, new_password_confirmation)
        selenium_driver.find_element(By.CSS_SELECTOR, "form div .btn-success").click()

    def assert_validation_errors(self, live_server, selenium_driver, account, password_input, password_confirm_input,
                                 error_password, error_password_confirm, is_server_side):
        user, password = account()[0]

        request_reset_account_via_website(live_server, selenium_driver, user.email)

        if is_server_side:
            self.submit_reset_password_form(live_server, selenium_driver, password_input, password_confirm_input)
        else:
            self.fill_reset_password_form(live_server, selenium_driver, password_input, password_confirm_input)

        assert get_form_error(selenium_driver, 1) == error_password
        assert get_form_error(selenium_driver, 2) == error_password_confirm
        assert_menu(selenium_driver)
        # Verifies that the user credentials keep the same
        authenticate(live_server, selenium_driver, user.username, password)

    def reset_account_with_different_passwords(self, live_server, selenium_driver, account, is_server_side):
        new_password = get_valid_password()
        diff_password = get_valid_password()

        while new_password == diff_password:
            diff_password = get_valid_password()

        self.assert_validation_errors(live_server, selenium_driver, account, new_password, diff_password,
                                      "", ERROR_NOT_CONFIRMED_PASSWORD, is_server_side)

    def reset_account_with_empty_field(self, live_server, selenium_driver, account, has_password,
                                       has_password_confirmation, expected_password_error,
                                       expected_confirm_password_error, is_server_side):
        random_password = get_valid_password()
        new_password = random_password if has_password else ""
        password_confirmation = random_password if has_password_confirmation else ""

        self.assert_validation_errors(live_server, selenium_driver, account, new_password, password_confirmation,
                                      expected_password_error, expected_confirm_password_error, is_server_side)

    def reset_account_with_invalid_password(self, live_server, selenium_driver, account, new_password, error_message,
                                            is_server_side):
        self.assert_validation_errors(live_server, selenium_driver, account, new_password, new_password,
                                      error_message, "", is_server_side)

    @pytest.mark.django_db
    def test_reset_account_form_rendering(self, live_server, selenium_driver, account):
        user, _ = account()[0]
        request_reset_account_via_website(live_server, selenium_driver, user.email)
        selenium_driver.get(get_reset_account_link())

        password_labels = selenium_driver.find_elements(By.ID, "id_new_password1_label")
        password_inputs = selenium_driver.find_elements(By.ID, "id_new_password1")
        confirmation_password_labels = selenium_driver.find_elements(By.ID, "id_new_password2_label")
        confirmation_input_labels = selenium_driver.find_elements(By.ID, "id_new_password2_label")
        submit_buttons = selenium_driver.find_elements(By.CSS_SELECTOR, "form div .btn-success")

        assert len(password_labels) == 1
        assert len(password_inputs) == 1
        assert len(confirmation_password_labels) == 1
        assert len(confirmation_input_labels) == 1
        assert len(submit_buttons) == 1
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_reset_account_invalid_link(self, live_server, selenium_driver, account):
        user, _ = account()[0]
        request_reset_account_via_website(live_server, selenium_driver, user.email)
        selenium_driver.get(get_reset_account_link() + get_random_string(5))

        alert_dangers = selenium_driver.find_elements(By.CLASS_NAME, "alert-danger")

        assert len(alert_dangers) == 1
        assert alert_dangers[0].text == "Invalid token!"
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_reset_account_different_passwords_server_side(self, live_server, selenium_driver, account):
        self.reset_account_with_different_passwords(live_server, selenium_driver, account, True)

    @pytest.mark.parametrize(
        "has_password, has_password_confirmation, expected_password_error, expected_password_confirmation_error", [
            (True, False, "", ERROR_REQUIRED_FIELD),
            (False, True, ERROR_REQUIRED_FIELD, ""),
            (False, False, ERROR_REQUIRED_FIELD, ERROR_REQUIRED_FIELD)
        ]
    )
    @pytest.mark.django_db
    def test_reset_account_require_passwords_server_side(self, live_server, selenium_driver, account,
                                                         has_password, has_password_confirmation,
                                                         expected_password_error, expected_password_confirmation_error):
        self.reset_account_with_empty_field(live_server, selenium_driver, account,
                                            has_password, has_password_confirmation,
                                            expected_password_error, expected_password_confirmation_error, True)

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
    def test_reset_account_invalid_password_server_side(self, live_server, selenium_driver, account,
                                                        new_password, error_message):
        self.reset_account_with_invalid_password(live_server, selenium_driver, account, new_password,
                                                 error_message, True)

    @pytest.mark.django_db
    def test_reset_account_different_passwords_client_side(self, live_server, selenium_driver, account):
        self.reset_account_with_different_passwords(live_server, selenium_driver, account, False)

    @pytest.mark.parametrize(
        "has_password, has_password_confirmation, expected_password_error, expected_confirm_password_error", [
            (True, False, "", "{}\n{}".format(ERROR_REQUIRED_FIELD, ERROR_NOT_CONFIRMED_PASSWORD)),
            (False, True, ALL_PASSWORD_ERRORS, ERROR_NOT_CONFIRMED_PASSWORD),
            (False, False, ALL_PASSWORD_ERRORS, ERROR_REQUIRED_FIELD)
        ]
    )
    @pytest.mark.django_db
    def test_reset_account_require_passwords_client_side(self, live_server, selenium_driver, account,
                                                         has_password, has_password_confirmation,
                                                         expected_password_error, expected_confirm_password_error):
        self.reset_account_with_empty_field(live_server, selenium_driver, account,
                                            has_password, has_password_confirmation,
                                            expected_password_error, expected_confirm_password_error, False)

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
    def test_reset_account_invalid_password_client_side(self, live_server, selenium_driver, account,
                                                        new_password, error_message):
        self.reset_account_with_invalid_password(live_server, selenium_driver, account, new_password,
                                                 error_message, False)

    @pytest.mark.django_db
    def test_reset_account_same_passwords(self, live_server, selenium_driver, account):
        user, _ = account()[0]
        request_reset_account_via_website(live_server, selenium_driver, user.email)

        new_password = get_valid_password()

        self.submit_reset_password_form(live_server, selenium_driver, new_password, new_password)

        alert_successes = selenium_driver.find_elements(By.CLASS_NAME, "alert-success")

        assert len(alert_successes) == 1
        assert alert_successes[0].text == "Password successfully updated!"
        assert_menu(selenium_driver)
        # Verifies if the user credentials changed
        authenticate(live_server, selenium_driver, user.username, new_password)

    @pytest.mark.django_db
    def test_reset_account_via_api_same_passwords(self, live_server, api_client, selenium_driver, account):
        user, password = account()[0]
        self.request_reset_account_via_api(api_client, user.email)

        new_password = get_valid_password()

        self.submit_reset_password_form(live_server, selenium_driver, new_password, new_password)

        alert_successes = selenium_driver.find_elements(By.CLASS_NAME, "alert-success")

        assert len(alert_successes) == 1
        assert alert_successes[0].text == "Password successfully updated!"
        assert_menu(selenium_driver)
        # Verifies if the user credentials changed
        authenticate(live_server, selenium_driver, user.username, new_password)