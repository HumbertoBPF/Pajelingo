import random
import time

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from languageschool.models import AppUser
from languageschool.tests.selenium.utils import assert_menu, authenticate, WARNING_REQUIRED_FIELD_HTML, \
    WARNING_EMAIL_WITH_SPACE_HTML, WARNING_REQUIRED_EMAIL_FIREFOX_HTML, get_form_error_message, submit_form_user
from languageschool.validation import ERROR_SPACE_IN_USERNAME, ERROR_LENGTH_PASSWORD, ERROR_NOT_CONFIRMED_PASSWORD, \
    ERROR_NOT_AVAILABLE_EMAIL, ERROR_NOT_AVAILABLE_USERNAME


class TestsProfileSelenium:
    @pytest.mark.django_db
    def test_profile_access_requires_authentication(self, live_server, selenium_driver):
        """
        Checks that users cannot access their profile without authentication
        """
        selenium_driver.get(live_server.url + reverse("account-profile"))
        warning_no_account = selenium_driver.find_element(By.ID, "warningNoAccount")

        assert warning_no_account.text == "Create an account to have profile information including game metrics and a place in our rankings."
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_profile_access_with_authenticated_user_without_scores(self, live_server, selenium_driver, account):
        """
        Checks that the credentials of users (username and email) are correctly rendered on their profile page
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-profile"))

        username = selenium_driver.find_element(By.ID, "username")
        email = selenium_driver.find_element(By.ID, "email")
        default_picture_filename = selenium_driver.find_element(By.ID, "defaultPicture").get_attribute("src")
        warning_no_scores = selenium_driver.find_element(By.ID, "warningNoScores")

        assert default_picture_filename == live_server.url + "/static/profile.jpg"
        assert username.text == "Username: {}".format(user.username)
        assert email.text == "Email: {}".format(user.email)
        assert warning_no_scores.text == "Play a game to have a history of your scores"
        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_profile_access_with_authenticated_user_with_scores(self, live_server, selenium_driver, account, score, games, languages):
        """
        Checks that the scores of users are correctly rendered in their profile page
        """
        user, password = account()[0]
        scores = score(users=[user], games=games, languages=languages).order_by('language')
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-profile"))

        username = selenium_driver.find_element(By.ID, "username")
        email = selenium_driver.find_element(By.ID, "email")
        default_picture_filename = selenium_driver.find_element(By.ID, "defaultPicture").get_attribute("src")
        header_score_tables = selenium_driver.find_element(By.TAG_NAME, "thead").find_element(By.TAG_NAME, "tr")
        row_scores = selenium_driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        assert default_picture_filename == live_server.url + "/static/profile.jpg"
        assert username.text == "Username: {}".format(user.username)
        assert email.text == "Email: {}".format(user.email)
        assert header_score_tables.text == "{} {} {}".format("Language", "Game", "Score")

        for i in range(len(row_scores)):
            score = scores[i]
            assert row_scores[i].text == "{} {} {}".format(score.language, score.game.game_name, score.score)

        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_update_account_form_requires_authentication(self, live_server, selenium_driver, account):
        """
        Checks that the page with the update account form requires authentication
        """
        selenium_driver.get(live_server.url + reverse("account-update-user"))
        assert selenium_driver.current_url == live_server.url + reverse("index")
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_update_account_form_rendering(self, live_server, selenium_driver, account):
        """
        Checks that the update account form renders correctly
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-update-user"))

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
        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_update_account_requires_authentication(self, live_server, selenium_driver):
        """
        Checks that the update account endpoint requires authentication
        """
        selenium_driver.get(live_server.url + reverse("account-do-update-user"))
        assert selenium_driver.current_url == live_server.url + reverse("index")
        assert_menu(selenium_driver, False)

    @pytest.mark.parametrize(
        "email, username, password, is_password_confirmed, field, accepted_messages", [
            (get_random_string(random.randint(1, 18)) + "@test.com", get_random_string(random.randint(1, 18)), "", True, "inputPassword", [WARNING_REQUIRED_FIELD_HTML]),
            (get_random_string(random.randint(1, 18)) + "@test.com", "", get_random_string(random.randint(6, 30)), True, "inputUsername", [WARNING_REQUIRED_FIELD_HTML]),
            ("", get_random_string(random.randint(1, 18)), get_random_string(random.randint(6, 30)), True, "inputEmail", [WARNING_REQUIRED_FIELD_HTML]),
            (get_random_string(random.randint(1, 9)) + " " + get_random_string(random.randint(1, 9)) + "@test.com", get_random_string(random.randint(1, 18)), get_random_string(random.randint(6, 30)), True, "inputEmail", [WARNING_EMAIL_WITH_SPACE_HTML, WARNING_REQUIRED_EMAIL_FIREFOX_HTML]),
            (get_random_string(random.randint(1, 18)) + "@test.com", get_random_string(random.randint(1, 9)) + " " + get_random_string(random.randint(1, 9)), get_random_string(random.randint(6, 30)), True, "alert-danger", [ERROR_SPACE_IN_USERNAME]),
            (get_random_string(random.randint(1, 18)) + "@test.com", get_random_string(random.randint(1, 18)), get_random_string(random.randint(1, 5)), True, "alert-danger", [ERROR_LENGTH_PASSWORD]),
            (get_random_string(random.randint(1, 18)) + "@test.com", get_random_string(random.randint(1, 18)), get_random_string(random.randint(31, 50)), True, "alert-danger", [ERROR_LENGTH_PASSWORD]),
            (get_random_string(random.randint(1, 18)) + "@test.com", get_random_string(random.randint(1, 18)), get_random_string(random.randint(6, 30)), False, "alert-danger", [ERROR_NOT_CONFIRMED_PASSWORD])
        ]
    )
    @pytest.mark.django_db
    def test_update_account_validation_error(self, live_server, selenium_driver, account, email, username, password, is_password_confirmed, field, accepted_messages):
        """
        Checks possible validation errors when submitting the update account form
        """
        user, user_password = account()[0]
        authenticate(live_server, selenium_driver, user.username, user_password)
        selenium_driver.get(live_server.url + reverse("account-update-user"))

        confirmation_password = password if is_password_confirmed else get_random_string(random.randint(6, 30))

        submit_form_user(selenium_driver, email, username, password, confirmation_password)

        is_valid_message = False

        for message in accepted_messages:
            is_valid_message = is_valid_message or (get_form_error_message(selenium_driver, field) == message)

        assert is_valid_message
        assert not User.objects.filter(id=user.id, username=username, email=email).exists()
        assert not AppUser.objects.filter(user__id=user.id, user__username=username, user__email=email).exists()
        assert_menu(selenium_driver, True)

    @pytest.mark.parametrize(
        "is_repeated_email, is_repeated_username", [
            (True, False),
            (False, True),
            (True, True)
        ]
    )
    @pytest.mark.django_db
    def test_update_account_with_non_available_credentials(self, live_server, selenium_driver, account, is_repeated_email, is_repeated_username):
        """
        Checks that users cannot use other users usernames and emails when updating their accounts
        """
        accounts = account(n=random.randint(2, 10))
        user, password = accounts[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-update-user"))

        repeated_email = random.choice(accounts[1:])[0].email
        repeated_username = random.choice(accounts[1:])[0].username

        email = repeated_email if is_repeated_email else get_random_string(random.randint(1, 18)) + "@test.com"
        username = repeated_username if is_repeated_username else get_random_string(random.randint(1, 18))
        password = get_random_string(random.randint(6, 30))

        submit_form_user(selenium_driver, email, username, password, password)

        alert_danger = selenium_driver.find_element(By.CLASS_NAME, "alert-danger")

        if is_repeated_email:
            assert alert_danger.text == ERROR_NOT_AVAILABLE_EMAIL
        elif is_repeated_username:
            assert alert_danger.text == ERROR_NOT_AVAILABLE_USERNAME
        # Checks that the authenticated user did not have its credentials changed
        assert not User.objects.filter(id=user.id, username=username, email=email).exists()
        assert not AppUser.objects.filter(user__id=user.id, user__username=username, user__email=email).exists()
        assert_menu(selenium_driver, True)

    @pytest.mark.parametrize(
        "is_same_email, is_same_username", [
            (True, False),
            (False, True),
            (True, True),
            (False, False)
        ]
    )
    @pytest.mark.django_db
    def test_update_account_with_valid_credentials(self, live_server, selenium_driver, account, is_same_email, is_same_username):
        """
        Checks that users can update their accounts using the current username and email
        """
        accounts = account(n=random.randint(2, 10))
        user, password = accounts[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-update-user"))

        email = user.email if is_same_email else get_random_string(random.randint(1, 18)) + "@test.com"
        username = user.username if is_same_username else get_random_string(random.randint(1, 18))
        password = get_random_string(random.randint(6, 30))

        submit_form_user(selenium_driver, email, username, password, password)
        # Checks if the users are redirected to their profile
        assert selenium_driver.current_url == live_server.url + reverse("account-profile")
        # Checks that the update was successful
        assert User.objects.filter(id=user.id, username=username, email=email).exists()
        assert AppUser.objects.filter(user__id=user.id, user__username=username, user__email=email).exists()
        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_delete_account_requires_authentication(self, live_server, selenium_driver, account):
        """
        Checks that users cannot delete other users by accessing the deletion endpoint from a browser
        """
        accounts = account(n=random.randint(5, 10))
        selenium_driver.get(live_server.url + reverse("account-delete-user"))
        assert len(accounts) == User.objects.count()
        assert_menu(selenium_driver, False)

    @pytest.mark.django_db
    def test_delete_account_dialog_is_shown(self, live_server, selenium_driver, account):
        """
        Checks that a dialog to confirm deletion is shown when users try to delete their accounts.
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-profile"))

        selenium_driver.find_element(By.ID, "deleteAccountButton").click()

        dialog_header = selenium_driver.find_element(By.ID, "deleteAccountDialogHeaderText")
        dialog_body = selenium_driver.find_element(By.ID, "deleteAccountDialogBodyText")
        confirm_button = selenium_driver.find_element(By.ID, "confirmDeletion")
        decline_button = selenium_driver.find_element(By.ID, "declineDeletion")
        # Time to render the text
        time.sleep(1)
        assert dialog_header.text == "Are you sure?"
        assert dialog_body.text == "Are you sure that you want to delete your profile? All information such as scores in the games is going to be permanently lost!"
        assert confirm_button.text == "Yes, I want to delete my profile"
        assert decline_button.text == "Decline"
        # Checks that the user still exists in database
        assert User.objects.filter(id=user.id).exists()
        assert AppUser.objects.filter(user__id=user.id).exists()
        assert_menu(selenium_driver, True)

    @pytest.mark.django_db
    def test_delete_account(self, live_server, selenium_driver, account):
        """
        Checks users deletion on profile page
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-profile"))

        selenium_driver.find_element(By.ID, "deleteAccountButton").click()
        # Waits "confirm deletion" button to appear to hit it
        wait = WebDriverWait(selenium_driver, 3)
        wait.until(EC.element_to_be_clickable((By.ID, "confirmDeletion"))).click()

        assert not User.objects.filter(id=user.id).exists()
        assert not AppUser.objects.filter(user__id=user.id).exists()
        assert_menu(selenium_driver, False)

    @pytest.mark.parametrize(
        "filename", [
            "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\pajelingo\\static\\test0.jfif",
            "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\pajelingo\\static\\test1.jpg"
        ]
    )
    @pytest.mark.django_db
    def test_change_profile_pic_valid_file(self, live_server, selenium_driver, account, filename):
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-profile"))

        picture_uploader = selenium_driver.find_element(By.ID, "id_picture")
        picture_uploader.send_keys(filename)
        selenium_driver.find_element(By.ID, "changePictureButton").click()

        assert AppUser.objects.filter(user__id=user.id).first().picture.url.endswith(filename.split(".")[1])
        assert_menu(selenium_driver, True)

    @pytest.mark.parametrize(
        "filename", [
            "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\pajelingo\\templates\\games\\article_game\\article_game_setup.html",
            "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\languageschool\\views\\games\\conjugation_game.py"
        ]
    )
    @pytest.mark.django_db
    def test_change_profile_pic_invalid_file(self, live_server, selenium_driver, account, filename):
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("account-profile"))

        picture_uploader = selenium_driver.find_element(By.ID, "id_picture")
        picture_uploader.send_keys(filename)
        selenium_driver.find_element(By.ID, "changePictureButton").click()

        assert not AppUser.objects.filter(user__id=user.id).first().picture
        assert_menu(selenium_driver, True)