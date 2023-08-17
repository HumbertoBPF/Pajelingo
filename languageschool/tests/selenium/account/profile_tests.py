import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import User
from languageschool.tests.selenium.utils import authenticate_user, assert_profile_language_filter, \
    assert_profile_scores, find_by_test_id, wait_for_redirect, assert_public_account_data, assert_private_account_data
from languageschool.tests.utils import attribute_user_badges
from pajelingo.settings import FRONT_END_URL

PROFILE_URL = f"{FRONT_END_URL}/profile"
TEST_ID_DELETE_ITEM = "delete-item"
TEST_ID_DELETE_DIALOG_INPUT = "confirm-delete-input"
TEST_ID_DELETE_DIALOG_CONFIRM_BUTTON = "delete-button"
TEST_ID_UPDATE_PICTURE_BUTTON = "update-picture-button"
TEST_ID_UPDATE_PICTURE_DIALOG_CONFIRM_BUTTON = "update-button"


@pytest.mark.django_db
def test_profile(live_server, selenium_driver, account):
    """
    Tests that the content of the profile page is displayed as expected, that is, that the username and email
    credentials as well as the "update profile picture", "edit account" and "delete account" button are displayed.
    """
    user, password = account()[0]
    attribute_user_badges()

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    assert_public_account_data(selenium_driver, user)
    assert_private_account_data(selenium_driver, user)


@pytest.mark.django_db
def test_profile_delete_account(live_server, selenium_driver, account):
    """
    Tests that deleting the profile works as expected, that is, a dialog is opened asking for confirmation and when
    users confirm, their account is deleted.
    """
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    delete_account_button = find_by_test_id(selenium_driver, TEST_ID_DELETE_ITEM)
    delete_account_button.click()

    delete_dialog_input = find_by_test_id(selenium_driver, TEST_ID_DELETE_DIALOG_INPUT).\
        find_element(By.CSS_SELECTOR, "input")
    delete_dialog_input.send_keys("permanently delete")

    delete_dialog_delete_button = find_by_test_id(selenium_driver, TEST_ID_DELETE_DIALOG_CONFIRM_BUTTON)
    delete_dialog_delete_button.click()

    wait_for_redirect(selenium_driver, f"{FRONT_END_URL}/login")

    assert not User.objects.filter(
        username=user.username,
        email=user.email
    ).exists()


@pytest.mark.django_db
def test_profile_update_profile_picture(live_server, selenium_driver, account):
    """
    Tests the update profile picture flow, that is, users must click on the "update profile picture" button, then
    a modal is opened asking for an image file. When an image file is provided and the users click on the "update"
    button, the users are redirected back to the profile page after having their profile picture updated.
    """
    user, password = account()[0]
    attribute_user_badges()

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    update_picture_button = find_by_test_id(selenium_driver, TEST_ID_UPDATE_PICTURE_BUTTON)
    update_picture_button.click()

    profile_picture_dialog_success_button = \
        find_by_test_id(selenium_driver, TEST_ID_UPDATE_PICTURE_DIALOG_CONFIRM_BUTTON)
    profile_picture_dialog_success_button.click()

    assert_public_account_data(selenium_driver, user)
    assert_private_account_data(selenium_driver, user)


@pytest.mark.django_db
def test_profile_user_scores(live_server, selenium_driver, account, languages, score):
    """
    Tests that the expected user scores are displayed on the profile page.
    """
    user, password = account()[0]
    random_language = random.choice(languages)
    score([user], languages)

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    assert_profile_language_filter(selenium_driver, languages)
    assert_profile_scores(selenium_driver, user, random_language)
