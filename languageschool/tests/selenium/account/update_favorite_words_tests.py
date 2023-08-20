import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Word, User
from languageschool.tests.selenium.utils import authenticate_user, find_element, scroll_to_element, \
    get_language_from_word_card, get_word_name_from_card_word, find_by_test_id
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_CARDS = (By.CSS_SELECTOR, "main .card")

TEST_ID_HEART_FILL_ICON = "[data-testid=\"heart-filled-icon\"]"
TEST_ID_HEART_ICON = "[data-testid=\"heart-icon\"]"


def wait_toggle_heart_icon(random_card, expected_locator):
    counter = 0
    toggled_icons = random_card.find_elements(By.CSS_SELECTOR, expected_locator)

    while (len(toggled_icons) == 0) and (counter < 100):
        toggled_icons = random_card.find_elements(By.CSS_SELECTOR, expected_locator)
        counter += 1


@pytest.mark.django_db
def test_favorite_words_toggle_favorite_word(live_server, selenium_driver, account):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "profile-dropdown").click()
    find_by_test_id(selenium_driver, "profile-item").click()
    find_by_test_id(selenium_driver, "favorite-item").click()

    find_element(selenium_driver, CSS_SELECTOR_CARDS)
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)

    language_name = get_language_from_word_card(random_card)
    word_name = get_word_name_from_card_word(random_card)

    word = Word.objects.filter(
        language__language_name=language_name,
        word_name=word_name
    ).first()

    if user.favorite_words.contains(word):
        heart_fill_icon = random_card.find_element(By.CSS_SELECTOR, TEST_ID_HEART_FILL_ICON)
        heart_fill_icon.click()
        wait_toggle_heart_icon(random_card, TEST_ID_HEART_ICON)
        assert not User.objects.get(id=user.id).favorite_words.contains(word)
    else:
        heart_non_fill_icon = random_card.find_element(By.CSS_SELECTOR, TEST_ID_HEART_ICON)
        heart_non_fill_icon.click()
        wait_toggle_heart_icon(random_card, TEST_ID_HEART_FILL_ICON)
        assert User.objects.get(id=user.id).favorite_words.contains(word)


@pytest.mark.django_db
def test_favorite_words_meaning_toggle_favorite_word(live_server, selenium_driver, account, words, meanings):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "profile-dropdown").click()
    find_by_test_id(selenium_driver, "profile-item").click()
    find_by_test_id(selenium_driver, "favorite-item").click()

    find_element(selenium_driver, CSS_SELECTOR_CARDS)
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)
    random_card.click()

    word_id = selenium_driver.current_url.split(FRONT_END_URL + "/meanings/")[1].split("#")[0]
    word = Word.objects.get(id=word_id)

    favorite_button = find_by_test_id(selenium_driver, "favorite-button")
    scroll_to_element(selenium_driver, favorite_button)

    if user.favorite_words.contains(word):
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        favorite_button.click()
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))
        assert not User.objects.get(id=user.id).favorite_words.contains(word)
    else:
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))
        favorite_button.click()
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        assert User.objects.get(id=user.id).favorite_words.contains(word)


@pytest.mark.django_db
def test_dictionary_toggle_favorite_word(live_server, selenium_driver, account, words, meanings):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "search-dropdown").click()
    find_by_test_id(selenium_driver, "dictionary-item").click()

    find_element(selenium_driver, CSS_SELECTOR_CARDS)
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)

    language_name = get_language_from_word_card(random_card)
    word_name = get_word_name_from_card_word(random_card)

    word = Word.objects.filter(
        language__language_name=language_name,
        word_name=word_name
    ).first()

    if user.favorite_words.contains(word):
        heart_fill_icon = random_card.find_element(By.CSS_SELECTOR, TEST_ID_HEART_FILL_ICON)
        heart_fill_icon.click()
        wait_toggle_heart_icon(random_card, TEST_ID_HEART_ICON)
        assert not User.objects.get(id=user.id).favorite_words.contains(word)
    else:
        heart_non_fill_icon = random_card.find_element(By.CSS_SELECTOR, TEST_ID_HEART_ICON)
        heart_non_fill_icon.click()
        wait_toggle_heart_icon(random_card, TEST_ID_HEART_FILL_ICON)
        assert User.objects.get(id=user.id).favorite_words.contains(word)


@pytest.mark.django_db
def test_dictionary_meaning_toggle_favorite_word(live_server, selenium_driver, account, words, meanings):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "search-dropdown").click()
    find_by_test_id(selenium_driver, "dictionary-item").click()

    find_element(selenium_driver, CSS_SELECTOR_CARDS)
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    random_card = random.choice(cards)
    random_card.click()

    word_id = selenium_driver.current_url.split(FRONT_END_URL + "/meanings/")[1].split("#")[0]
    word = Word.objects.get(id=word_id)

    favorite_button = find_by_test_id(selenium_driver, "favorite-button")
    scroll_to_element(selenium_driver, favorite_button)

    if user.favorite_words.contains(word):
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        favorite_button.click()
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))
        assert not User.objects.get(id=user.id).favorite_words.contains(word)
    else:
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart-fill"))
        favorite_button.click()
        find_element(selenium_driver, (By.CSS_SELECTOR, "main .btn-info .bi-heart"))
        assert User.objects.get(id=user.id).favorite_words.contains(word)
